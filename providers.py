import time

import pyautogui

from helpers import Profile, Image
from cv_helpers import cv2_detect_main_pic

class DatingProvider(object):

    def __init__(self, name = "base_provider"):
        self.central_pic_region = None
        self.url = ""
        self.name = name
        self.current_profile = Profile(provider_name=self.name)

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

        self.current_profile = Profile(provider_name=self.name)

    def handle_yes_no_image(self, rating: bool):

        pic = self.get_central_pic()

        if pic:
            img_obj = Image(rating=rating, img=pic)
            self.current_profile.add_image(img_obj)

        self.get_next_pic()

    def swipe_right(self):

        pyautogui.press('right')
    
    def swipe_left(self):

        pyautogui.press('left')

    def get_next_pic(self):

        pyautogui.press('space')

    def get_central_pic(self):
        pass

class BadooProvider(DatingProvider):

    def __init__(self):
        super().__init__(name = "badoo") 
        self.url = "https://badoo.com/encounters"

    def get_central_pic(self):

        if not self.central_pic_region:

            self.central_pic_region = cv2_detect_main_pic()

        if not self.central_pic_region:
            return None
        else: 
            return pyautogui.screenshot(region=self.central_pic_region.as_tuple())

class TinderProvider(DatingProvider):

    def __init__(self):
        super().__init__(name = "tinder") 
        self.url = "https://tinder.com/app/recs"

    def get_central_pic(self):

        if not self.central_pic_region:

            pyautogui.press('esc')
            time.sleep(1)
            self.central_pic_region = cv2_detect_main_pic()
            if self.central_pic_region: # crop tinder pics
                self.central_pic_region.width -= 15
                self.central_pic_region.height -= 60
            pyautogui.press('space')
            time.sleep(1)

        if not self.central_pic_region:
            return None
        else: 
            return pyautogui.screenshot(region=self.central_pic_region.as_tuple())
