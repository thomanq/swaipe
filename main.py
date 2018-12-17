import os
import time
from random import random, randint, uniform
import tkinter as tk
import configparser
import threading
import datetime

from PIL import Image, ImageGrab
import pyautogui
from pynput.keyboard import KeyCode, Key, Listener
import cv2
import numpy as np

root = tk.Tk()

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

OPENCV_DATA_PATH = os.path.join(os.path.dirname(cv2.__file__), "data")

BADOO_BUTTONS = cv2.imread(os.path.join(ASSETS_DIR, "badoo_buttons.png"))
BADOO_BUTTON_H = BADOO_BUTTON_W = 75
BADOO_BUTTON_SPACING = 10

BADOO_URL = "https://badoo.com/encounters"

def open_url(url):
    os.system("start " + url)

def locate(needleImage, haystackImage, method=cv2.TM_CCOEFF_NORMED, threshold = 0.5):
    ''' OpenCV matchTemplate method wrapper
        Available methods:
            cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED
    '''
    
    res = cv2.matchTemplate(haystackImage,needleImage, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    _, width, height = needleImage.shape[::-1]

    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left_x = min_loc[0]
        top_left_y = min_loc[1]
    else:
        top_left_x = max_loc[0]
        top_left_y = max_loc[1]
    
    if max_val > threshold: 
        return (top_left_x, top_left_y, width, height)
    else: 
        return None

def get_yes_no_locations():
    while True:

        screen = np.asarray(ImageGrab.grab())
        badoo_buttons = locate(BADOO_BUTTONS, screen)
        if badoo_buttons: 
            left = badoo_buttons[0]
            top = badoo_buttons[1]
            no_location = (left, top, BADOO_BUTTON_W, BADOO_BUTTON_H)
            yes_location = (left + BADOO_BUTTON_W * 2 + BADOO_BUTTON_SPACING * 2, top, BADOO_BUTTON_W, BADOO_BUTTON_H)

            return yes_location, no_location

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def get_corners(region):
    left, top, w, h = region
    topleft = Point(left, top)
    topright = Point(left + w, top)
    bottom_left = Point(left, top + h)
    bottom_right = Point(left + w, top + h)

    return topleft, topright, bottom_left, bottom_right

def point_in_region(point, region):
    left, top, w, h = region
     
    return left <= point.x <= left + w \
         and top <= point.y <= top + h

def overlap(region_1, region_2):

    left_2, top_2, w_2, h_2 = region_2

    for corner in get_corners(region_1):
         if point_in_region(corner, region_2):
            return True

    return False

def click(location):
    left, top, width, height = location
    xpos = randint(left + int(width/3), left + width - int(width/3))
    ypos = randint(top + int(height/3), top + height - int(height/3))

    click_region = (left+int(width/3), top+int(height/3), int(width/3), int(height/3))
    cursor_position = Point(*pyautogui.position())

    if not point_in_region(cursor_position, click_region):
        pyautogui.moveTo(xpos, ypos, duration=uniform(0.2, 0.5))

    pyautogui.click()

def get_central_pic(no_location, root):

    SCREEN_WIDTH = root.winfo_screenwidth()
    SCREEN_HEIGHT = root.winfo_screenheight()

    window_width = root.winfo_width()
    window_height = root.winfo_height()

    window_left = root.winfo_x()
    window_top = root.winfo_y()

    window_region = (window_left, window_top, window_width, window_height)

    offset_top = 110
    offset_bottom = 30
    offset_from_no_button = 50
    badoo_central_image_width = 520   

    picture_region = (no_location[0] - offset_from_no_button - badoo_central_image_width, 
                     offset_top, 
                     badoo_central_image_width, 
                     SCREEN_HEIGHT - offset_top - offset_bottom)

    if overlap(window_region, picture_region):
        # move window out of he way
        root.geometry("+10+10")
        time.sleep(0.5)

    image = pyautogui.screenshot(region=picture_region)

    return image, picture_region

class Image(object):
    def __init__(self, rating=False, img=None):
        self.rating = rating
        self.img = img

    def __eq__(self, other):
        if isinstance(other, Image):
            return self.img == other.img
        return NotImplemented

class Profile(object):
    
    def __init__(self, rating=False):
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
                
                line = f"image,{filename},{int(unique_img.rating)}\n"
                annotations.write(line)

            img_ratings = '"({})"'.format(",".join([str(int(unique_img.rating)) for unique_img in umique_imgs]))
            line = f"profile,{basename},{img_ratings},{int(self.rating)}\n"
            annotations.write(line)
            

def handle_yes_no_image(rating, get_main_pic):
    global current_profile

    if not current_profile:
        current_profile = Profile()

    pic, central_picture_region = get_main_pic()
    img_obj = Image(rating=rating, img=pic)

    current_profile.add_image(img_obj)
    click(central_picture_region)

def handle_yes_no_profile(rating, location, get_main_pic):
    global current_profile

    if not current_profile:
        current_profile = Profile()

    pic, central_picture_region = get_main_pic()
    img_obj = Image(rating=rating, img=pic)

    current_profile.add_image(img_obj)
    current_profile.rating = rating
    current_profile.serialize()

    click(location)
    current_profile = Profile()


def init_GUI(root, settings):

    root.title('Swaipe')
    frame = tk.Frame(root)
    frame.pack()

    button_badoo = tk.Button(frame, 
                    text="Go to Badoo",
                    command=lambda: open_url(BADOO_URL))
    button_badoo.grid(row=0, column=0, padx=5, pady=5, ipadx=10)

    picture_label_text = f"Picture:  [Yes '{settings.yes_pic_shortcut}'] [No '{settings.no_pic_shortcut}']"

    picture_label = tk.Label(frame, text=picture_label_text)
    picture_label.grid(row=1, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

    overall_label_text = f"Overall:  [Yes '{settings.yes_overall_shortcut}'] [No '{settings.no_overall_shortcut}']"

    overall_label = tk.Label(frame, text=overall_label_text)
    overall_label.grid(row=2, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

    button_start_stop = tk.Button(frame, 
                    text="Start")
    button_start_stop.grid(row=3, column=0,padx=5, pady=5, ipadx=20)

    root.wm_attributes("-topmost", 1)

    root.mainloop()

def is_modifier(key):
    return key in (Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr, Key.cmd, Key.cmd_l, Key.cmd_r, Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.shift, Key.shift_l, Key.shift_r)

def key_to_string(key):
    keys = {Key.alt: "alt", Key.alt_l: "alt_l", Key.alt_r: "alt_r", Key.alt_gr: "alt_gr", Key.backspace: "backspace", Key.caps_lock: "caps_lock", Key.cmd: "cmd", Key.cmd_l: "cmd_l", Key.cmd_r: "cmd_r", Key.ctrl: "ctrl", Key.ctrl_l: "ctrl_l", Key.ctrl_r: "ctrl_r", Key.delete: "delete", Key.down: "down", Key.end: "end", Key.enter: "enter", Key.esc: "esc", Key.f1: "f1", Key.f2: "f2", Key.f3: "f3", Key.f4: "f4", Key.f5: "f5", Key.f6: "f6", Key.f7: "f7", Key.f8: "f8", Key.f9: "f9", Key.f10: "f10", Key.f11: "f11", Key.f12: "f12", Key.f13: "f13", Key.f14: "f14", Key.f15: "f15", Key.f16: "f16", Key.f17: "f17", Key.f18: "f18", Key.f19: "f19", Key.f20: "f20", Key.home: "home", Key.left: "left", Key.page_down: "page_down", Key.page_up: "page_up", Key.right: "right", Key.shift: "shift", Key.shift_l: "shift_l", Key.shift_r: "shift_r", Key.space: "space", Key.tab: "tab", Key.up: "up", Key.insert: "insert", Key.menu: "menu", Key.num_lock: "num_lock", Key.pause: "pause", Key.print_screen: "print_screen", Key.scroll_lock: "scroll_lock"}

    if key in keys: 
        return keys[key]    
    else:
        return None

def sc_base(shortcut):
    if shortcut == "+" or (len(shortcut) > 1 and shortcut[-1] == "+"):
        return "+"
    elif len(shortcut.split("+")) == 2:
        return shortcut.split("+")[1] 
    else:
        return shortcut

def sc_modifier(shortcut):
    if len(shortcut.split("+")) == 2:
        return extend_modifier(shortcut.split("+")[0])
    else: 
        return [None]

def extend_modifier(shortcut):
    '''Match left and right modifiers witch main modifier name'''

    if shortcut in ("alt", "cmd", "ctrl", "shift"):
        return [shortcut, shortcut + "_l", shortcut + "_r"]
    else:
        return [shortcut]

def on_key_press(key):
    global current_modifier

    if is_modifier(key):
        current_modifier = key

def on_key_release(key, yes_location, no_location, root):
    global current_modifier

    get_main_pic = lambda: get_central_pic(no_location, root)

    if is_modifier(key):
        current_modifier = None

    else:
        if key_to_string(current_modifier) in sc_modifier(settings.yes_pic_shortcut) \
        and (key_to_string(key) == sc_base(settings.yes_pic_shortcut) \
            or key == KeyCode.from_char(sc_base(settings.yes_pic_shortcut))):
                # I like the picture
                handle_yes_no_image(True, get_main_pic)

        elif key_to_string(current_modifier) in sc_modifier(settings.no_pic_shortcut) \
        and (key_to_string(key) == sc_base(settings.no_pic_shortcut) \
          or key == KeyCode.from_char(sc_base(settings.no_pic_shortcut))):
                # I don't like the picture
                handle_yes_no_image(False, get_main_pic)

        elif key_to_string(current_modifier) in sc_modifier(settings.yes_overall_shortcut) \
        and (key_to_string(key) == sc_base(settings.yes_overall_shortcut) \
          or key == KeyCode.from_char(sc_base(settings.yes_overall_shortcut))):
                # I like the profile
                handle_yes_no_profile(True, yes_location, get_main_pic)

        elif key_to_string(current_modifier) in sc_modifier(settings.no_overall_shortcut) \
        and (key_to_string(key) == sc_base(settings.no_overall_shortcut) \
          or key == KeyCode.from_char(sc_base(settings.no_overall_shortcut))):
                # I don't like the profile
                handle_yes_no_profile(False, no_location, get_main_pic)

class Settings:

    def __init__(self):
        settings = configparser.ConfigParser()
        settings.read_file(open(os.path.join(ROOT_DIR,"settings.cfg"), encoding="utf8"))

        self.yes_pic_shortcut = settings["Keyboard Shotcuts"]["I like the picture"]
        self.no_pic_shortcut = settings["Keyboard Shotcuts"]["I don't like the picture"]

        self.yes_overall_shortcut = settings["Keyboard Shotcuts"]["I like the profile"]
        self.no_overall_shortcut = settings["Keyboard Shotcuts"]["I don't like the profile"]
        
def detect_face(img_path):

    frontalface_alt_xml_path  = os.path.join(OPENCV_DATA_PATH, "haarcascade_frontalface_alt.xml")
    haarcascade_eye  = os.path.join(OPENCV_DATA_PATH, "haarcascade_eye.xml")
    haarcascade_fullbody  = os.path.join(OPENCV_DATA_PATH, "haarcascade_lowerbody.xml")

    face_cascade = cv2.CascadeClassifier(frontalface_alt_xml_path)
    eye_cascade = cv2.CascadeClassifier(haarcascade_eye)
    fullbody_cascade = cv2.CascadeClassifier(haarcascade_fullbody)

    img = cv2.imread(img_path)
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray_img)
    eyes = eye_cascade.detectMultiScale(gray_img)
    fullbody = fullbody_cascade.detectMultiScale(gray_img)

    # for (x,y,w,h) in faces:
    #     img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # print(faces)

def listen_to_keyboard():
    yes_location, no_location = None, None
    yes_location, no_location = get_yes_no_locations()

    with Listener(on_press=on_key_press, on_release= lambda key: on_key_release(key, yes_location, no_location, root)) as listener:
        global current_modifier, current_profile
        current_modifier, current_profile = None, None
        listener.join()


if __name__ == "__main__":

    settings = Settings()

    keyboard_hotkeys_thread = threading.Thread(target=listen_to_keyboard)
    keyboard_hotkeys_thread.daemon = True
    keyboard_hotkeys_thread.start()

    init_GUI(root, settings)
