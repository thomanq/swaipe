import datetime
import time
import threading
import os
import configparser

import pyautogui

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

class Image(object):
    def __init__(self, rating=False, img=None):
        self.rating = rating
        self.img = img

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.img == other.img
        return NotImplemented


class Profile(object):
    def __init__(self, rating=False, provider_name="provider_unknown", automator_name="automator_unknown"):
        self.provider_name = provider_name
        self.automator_name = automator_name
        self.rating = rating
        self.imgs = []

    def add_image(self, img):
        self.imgs.append(img)
    
    def serialize(self):
        PROFILE_PICS_DIR = os.path.join(ROOT_DIR, "profile_pictures")
        ANNOTATION_FILE_PATH = os.path.join(PROFILE_PICS_DIR, "annotations.csv")

        basename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        unique_imgs = []
        for img in self.imgs:
            if img not in unique_imgs:
                unique_imgs.append(img)

        with open(ANNOTATION_FILE_PATH, "a", encoding="utf-8") as annotations:

            for index, unique_img in enumerate(unique_imgs):
                filename = f"{basename}_{index+1}.jpg"
                filepath = os.path.join(PROFILE_PICS_DIR, filename)

                unique_img.img.save(filepath)
                
                line = f'image,{filename},{int(unique_img.rating)},"{self.provider_name}","{self.automator_name}"\n'
                annotations.write(line)

            img_ratings = '"({})"'.format(",".join([str(int(unique_img.rating)) for unique_img in unique_imgs]))
            line = f'profile,{basename},{int(self.rating)},"{self.provider_name}","{self.automator_name}",{img_ratings}\n'
            annotations.write(line)

class Settings:
    def __init__(self):
        settings = configparser.ConfigParser()
        settings.read_file(open(os.path.join(ROOT_DIR,"settings.cfg"), encoding="utf8"))

        self.yes_pic_shortcut = settings["Keyboard Shotcuts"]["I like the picture"]
        self.no_pic_shortcut = settings["Keyboard Shotcuts"]["I don't like the picture"]

        self.yes_profile_shortcut = settings["Keyboard Shotcuts"]["I like the profile"]
        self.no_profile_shortcut = settings["Keyboard Shotcuts"]["I don't like the profile"]

        self.select_tinder_provider = settings["Keyboard Shotcuts"]["Select tinder provider"]
        self.select_badoo_provider = settings["Keyboard Shotcuts"]["Select badoo provider"]

        self.go_to_tinder = settings["Keyboard Shotcuts"]["Go to tinder"]
        self.go_to_badoo = settings["Keyboard Shotcuts"]["Go to badoo"]

        self.start_stop_automator = settings["Keyboard Shotcuts"]["Start / stop automator"]
        self.choose_next_automator = settings["Keyboard Shotcuts"]["Choose next automator"]
        self.choose_previous_automator = settings["Keyboard Shotcuts"]["Choose previous automator"]

        self.automator_max_choice_limit_add_1 = settings["Keyboard Shotcuts"]["Automator +1 to max limit"]
        self.automator_max_choice_limit_add_10 = settings["Keyboard Shotcuts"]["Automator +10 to max limit"]
        self.automator_max_choice_limit_subtract_1 = settings["Keyboard Shotcuts"]["Automator -1 to max limit"]
        self.automator_max_choice_limit_subtract_10 = settings["Keyboard Shotcuts"]["Automator -10 to max limit"]

        self.automator_yes_rate_add_1_percent = settings["Keyboard Shotcuts"]["Automator +1% to yes percentage"]
        self.automator_yes_rate_subtract_1_percent = settings["Keyboard Shotcuts"]["Automator -1% to yes percentage"]        

class Session:
    def __init__(self, gui=None, provider=None, automators=[None]):
        self.current_key_modifier = None
        self.gui = gui
        self.provider = provider
        if self.provider:
            self.gui.update_selected_provider_text(self.provider.name)
        self.automators = automators if len(automators) > 0 else [None]
        self.automator = self.automators[0]
        if self.automator:
            self.automator.set_provider(self.provider)
            self.gui_update_selected_automator_text()
        self.automator_index = 0

    def next_automator(self):
        new_automator_index = self.automator_index + 1 if self.automator_index + 1 < len(self.automators) else 0
        self.choose_automator(new_automator_index)

    def previous_automator(self):
        new_automator_index = self.automator_index - 1 if self.automator_index - 1 >= 0 else len(self.automators) -1
        self.choose_automator(new_automator_index)

    def choose_automator(self, new_automator_index: int):
        if self.automator:
            if new_automator_index != self.automator_index:
                self.automator_index = new_automator_index
                self.automator.stop()
                self.automator = self.automators[self.automator_index]
                self.automator.set_provider(self.provider)
                self.gui_update_selected_automator_text()

    def change_provider(self, provider):
        self.automator.stop()
        self.provider = provider
        self.automator.set_provider(self.provider)
        self.gui.update_selected_provider_text(self.provider.name)
        self.gui_update_selected_automator_text()

    def gui_update_selected_automator_text(self):

            # stops the currently running check_ui_update_thread daemon
            self.ui_update_running = False
            time.sleep(0.5)

            check_ui_update_thread = threading.Thread(target=self.check_automator_update_ui)
            check_ui_update_thread.daemon = True
            check_ui_update_thread.start()

    def check_automator_update_ui(self):
        '''
            Deamon checks whether the Automator properties have changed.
            If so, it updates the UI
        '''

        first_run = True
        self.ui_update_running = True

        while True:
            if first_run or \
               automator_max_choices != self.automator.max_choice_limit or \
               automator_num_choices != self.automator.num_choices or \
               automator_is_running != self.automator.is_running or \
               automator_yes_rate_goal != self.automator.yes_rate_goal:

                self.gui.update_selected_automator_text(self.automator)

                automator_max_choices = self.automator.max_choice_limit
                automator_num_choices = self.automator.num_choices
                automator_is_running = self.automator.is_running
                automator_yes_rate_goal = self.automator.yes_rate_goal

                first_run = False

            if not self.ui_update_running:
                break

            time.sleep(0.1)

class Region:
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def as_tuple(self):
        return (self.left, self.top, self.width, self.height)

def open_url(url):
    os.system("start " + url)
