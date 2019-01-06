import time

import pyautogui
import numpy as np
from PIL import ImageGrab

from helpers import Profile, Image
from cv_helpers import cv2_detect_main_pic

class DatingProvider(object):

    def __init__(self, name = "base_provider", gui = None):
        self.central_pic_region = None
        self.url = ""
        self.name = name
        self.gui = gui
        self.automator_name = "manual"
        self.current_profile = Profile(provider_name=self.name, automator_name=self.automator_name)

    def set_automator_name(self, automator_name):
        self.automator_name = automator_name
        self.current_profile.automator_name = automator_name

    def handle_yes_no_profile(self, rating: bool):

        pic = self.get_central_pic()

        if pic:
            img_obj = Image(rating=rating, img=pic)
            self.current_profile.add_image(img_obj)
            self.current_profile.rating = rating
            self.current_profile.serialize()

        if rating:
            self.swipe_right()
        else:
            self.swipe_left()

        self.current_profile = Profile(provider_name=self.name, automator_name=self.automator_name)

    def handle_yes_no_image(self, rating: bool):

        pic = self.get_central_pic()

        if pic:
            img_obj = Image(rating=rating, img=pic)
            self.current_profile.add_image(img_obj)

        self.get_next_pic()

    def swipe_right(self):

        self.press('right')
    
    def swipe_left(self):

        self.press('left')

    def get_next_pic(self):

        self.press('space')

    def press(self, key: str):

        if self.gui.has_focus():
            self.gui.set_focus(self.name)

        pyautogui.press(key)

    def get_central_pic(self):
        pass
    
    def take_screenshot_of_region(self, region):
        self.gui.hide()
        screenshot = pyautogui.screenshot(region=region)
        self.gui.show()

        return screenshot

    def image_grab(self):
        self.gui.hide()
        image = np.asarray(ImageGrab.grab()).copy()
        self.gui.show()

        return image

class BadooProvider(DatingProvider):

    def __init__(self, name = "Badoo", gui=None):
        super().__init__(name = name, gui = gui) 
        self.url = "https://badoo.com/encounters"

    def get_central_pic(self):

        if not self.central_pic_region:

            image_grab = self.image_grab()
            self.central_pic_region = cv2_detect_main_pic(image_grab)

        if not self.central_pic_region:
            return None
        else: 
            return self.take_screenshot_of_region(self.central_pic_region.as_tuple())

class TinderProvider(DatingProvider):

    def __init__(self, name = "Tinder", gui=None):
        super().__init__(name = name, gui = gui) 
        self.url = "https://tinder.com/app/recs"
        self.is_current_pic_escaped = True

    def get_central_pic(self):

        if not self.central_pic_region:

            self.press('esc')
            time.sleep(0.5)
            image_grab = self.image_grab()
            self.central_pic_region = cv2_detect_main_pic(image_grab)
            if self.central_pic_region: # crop tinder pics
                self.central_pic_region.width -= 15
                self.central_pic_region.height -= 60
            self.press('space')
            self.is_current_pic_escaped = False
            time.sleep(1)

        if not self.central_pic_region:
            return None
        else: 
            return self.take_screenshot_of_region(self.central_pic_region.as_tuple())

    def get_next_pic(self):
        self.press('space')

        if self.is_current_pic_escaped:
             time.sleep(0.5)
             self.press('space')
             self.is_current_pic_escaped = False

    def handle_yes_no_profile(self, rating: bool):
        super().handle_yes_no_profile(rating)
        self.is_current_pic_escaped = True
