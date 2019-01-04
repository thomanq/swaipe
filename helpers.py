import datetime
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
    def __init__(self, rating=False, provider_name="provider_unknown"):
        self.provider_name = provider_name
        self.rating = rating
        self.imgs = []

    def add_image(self, img):
        self.imgs.append(img)
    
    def serialize(self):
        PROFILE_PICS_DIR = os.path.join(ROOT_DIR, "profile_pictures")
        ANNOTATION_FILE_PATH = os.path.join(PROFILE_PICS_DIR, "annotations.csv")

        basename = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        umique_imgs = []
        for img in self.imgs:
            if img not in umique_imgs:
                umique_imgs.append(img)

        with open(ANNOTATION_FILE_PATH, "a", encoding="utf-8") as annotations:

            for index, unique_img in enumerate(umique_imgs):
                filename = f"{basename}_{index+1}.png"
                filepath = os.path.join(PROFILE_PICS_DIR, filename)

                unique_img.img.save(filepath)
                
                line = f"image,{filename},{int(unique_img.rating)},{self.provider_name}\n"
                annotations.write(line)

            img_ratings = '"({})"'.format(",".join([str(int(unique_img.rating)) for unique_img in umique_imgs]))
            line = f"profile,{basename},{img_ratings},{int(self.rating)},{self.provider_name}\n"
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

class Session:
    def __init__(self, gui=None, provider=None):
        self.provider = provider
        self.gui = gui
        self.current_key_modifier = None

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
