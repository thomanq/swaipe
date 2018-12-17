import tkinter as tk
import threading

from pynput.keyboard import KeyCode, Key, Listener

from gui import GUI
from keys import *
from providers import BadooProvider, TinderProvider
from helpers import *

def on_key_press(key, session: Session):

    if is_modifier(key):
        session.current_key_modifier = key

def on_key_release(key, session: Session):

    if is_modifier(key):
        session.current_key_modifier =  None

    else:
        modifier = session.current_key_modifier

        if is_setting_shortcut(key, modifier, settings.yes_pic_shortcut):
                # I like the picture
                session.provider.handle_yes_no_image(True)

        elif is_setting_shortcut(key, modifier, settings.no_pic_shortcut):
                # I don't like the picture
                session.provider.handle_yes_no_image(False)

        elif is_setting_shortcut(key, modifier, settings.yes_overall_shortcut):
                # I like the profile
                session.provider.handle_yes_no_profile(True)

        elif is_setting_shortcut(key, modifier, settings.no_overall_shortcut):
                # I don't like the profile
                session.provider.handle_yes_no_profile(False)

        elif is_setting_shortcut(key, modifier, settings.select_badoo_provider):
                # Reset provider to Badoo provider
                session.provider = BadooProvider()
                session.gui.update_selected_provider_text("Badoo")

        elif is_setting_shortcut(key, modifier, settings.select_tinder_provider):
                # Reset provider to Tinder provider
                session.provider = TinderProvider()
                session.gui.update_selected_provider_text("Tinder")

        elif is_setting_shortcut(key, modifier, settings.go_to_badoo):
                # Go to Badoo website
                open_url(BadooProvider().url)

        elif is_setting_shortcut(key, modifier, settings.go_to_tinder):
                # Go to Tinder website
                open_url(TinderProvider().url)

def listen_to_keyboard():

    with Listener(on_press= lambda key: on_key_press(key, session),
         on_release= lambda key: on_key_release(key, session)) as listener:
        listener.join()

if __name__ == "__main__":

    settings = Settings()

    root = tk.Tk()
    gui = GUI(root, settings)

    session = Session(gui=gui, provider=BadooProvider())

    keyboard_hotkeys_thread = threading.Thread(target=listen_to_keyboard)
    keyboard_hotkeys_thread.daemon = True
    keyboard_hotkeys_thread.start()

    root.mainloop()
