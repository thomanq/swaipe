import tkinter as tk
import threading

from pynput.keyboard import KeyCode, Key, Listener

from gui import GUI
from keys import *
from providers import BadooProvider, BadooProvider123, TinderProvider
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
            # Reset provider to Badoo provider : toggles between available Badoo providers
            badoo_providers_classes = [BadooProvider123, BadooProvider]
            for badoo_provider_class in badoo_providers_classes:
                if badoo_provider_class != session.provider.__class__:
                    session.change_provider(badoo_provider_class(gui=session.gui))
                    break

        elif is_setting_shortcut(key, modifier, settings.select_tinder_provider):
            # Reset provider to Tinder provider
            session.change_provider(TinderProvider(gui=session.gui))

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

        # Update automator parameters : max_choice_limit and yes_rate_goal
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_add_1):
            session.automator.update_max_choice_limit(1)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_add_10):
            session.automator.update_max_choice_limit(10)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_subtract_1):
            session.automator.update_max_choice_limit(-1)
        elif is_setting_shortcut(key, modifier, settings.automator_max_choice_limit_subtract_10):
            session.automator.update_max_choice_limit(-10)
        elif is_setting_shortcut(key, modifier, settings.automator_yes_rate_add_1_percent):
            session.automator.update_yes_rate_goal(0.01)
        elif is_setting_shortcut(key, modifier, settings.automator_yes_rate_subtract_1_percent):
            session.automator.update_yes_rate_goal(-0.01)

        elif is_setting_shortcut(key, modifier, settings.toggle_hide_show_window):
            if session.gui.is_visible:
                session.gui.hide()
            else:
                session.gui.show()

def listen_to_keyboard():

    with Listener(on_press= lambda key: on_key_press(key, session),
         on_release= lambda key: on_key_release(key, session)) as listener:
        listener.join()

if __name__ == "__main__":

    settings = Settings()

    root = tk.Tk()
    root.wait_visibility()
    gui = GUI(root, settings)

    session = Session(gui=gui, provider=TinderProvider(gui=gui), automators=[RandomAutomator(yes_rate_goal=0.7), RandomAutomator(name="Limited Random Automator", max_choice_limit=50)])

    keyboard_hotkeys_thread = threading.Thread(target=listen_to_keyboard)
    keyboard_hotkeys_thread.daemon = True
    keyboard_hotkeys_thread.start()

    root.mainloop()
