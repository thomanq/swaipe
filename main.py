import tkinter as tk
import threading

from pynput.keyboard import KeyCode, Key, Listener

from gui import GUI
from keys import *
from providers import BadooProvider, TinderProvider
from automators import Automator, RandomAutomator
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
            if not session.automator.is_running:
                # I like the picture
                session.provider.handle_yes_no_image(True)

        elif is_setting_shortcut(key, modifier, settings.no_pic_shortcut):
            if not session.automator.is_running:
                # I don't like the picture
                session.provider.handle_yes_no_image(False)

        elif is_setting_shortcut(key, modifier, settings.yes_profile_shortcut):
            if not session.automator.is_running:
                # I like the profile
                session.provider.handle_yes_no_profile(True)

        elif is_setting_shortcut(key, modifier, settings.no_profile_shortcut):
            if not session.automator.is_running:
                # I don't like the profile
                session.provider.handle_yes_no_profile(False)

        elif is_setting_shortcut(key, modifier, settings.select_badoo_provider):
            # Reset provider to Badoo provider
            session.change_provider(BadooProvider())

        elif is_setting_shortcut(key, modifier, settings.select_tinder_provider):
            # Reset provider to Tinder provider
            session.change_provider(TinderProvider())

        elif is_setting_shortcut(key, modifier, settings.go_to_badoo):
            # Go to Badoo website
            open_url(BadooProvider().url)

        elif is_setting_shortcut(key, modifier, settings.go_to_tinder):
            # Go to Tinder website
            open_url(TinderProvider().url)

        elif is_setting_shortcut(key, modifier, settings.start_stop_automator):
            # Toggle start / stop automator
            session.automator.toggle_start_stop()
            session.gui.update_selected_automator_text(session.automator)
        
        elif is_setting_shortcut(key, modifier, settings.choose_next_automator):
            # Choose next available automator
            session.next_automator()

        elif is_setting_shortcut(key, modifier, settings.choose_previous_automator):
            # Choose previous available automator
            session.previous_automator()

        # Update de max number choice limit for the automator
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_add_1):
            session.automator.update_max_choice_limit(1)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_add_10):
            session.automator.update_max_choice_limit(10)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_subtract_1):
            session.automator.update_max_choice_limit(-1)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_subtract_10):
            session.automator.update_max_choice_limit(-10)

def listen_to_keyboard():

    with Listener(on_press= lambda key: on_key_press(key, session),
         on_release= lambda key: on_key_release(key, session)) as listener:
        listener.join()

if __name__ == "__main__":

    settings = Settings()

    root = tk.Tk()
    gui = GUI(root, settings)

    session = Session(gui=gui, provider=BadooProvider(), automators=[RandomAutomator(), RandomAutomator("bob"), Automator("b"), Automator("c")])

    keyboard_hotkeys_thread = threading.Thread(target=listen_to_keyboard)
    keyboard_hotkeys_thread.daemon = True
    keyboard_hotkeys_thread.start()

    root.mainloop()
