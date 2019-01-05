import time
import threading


def only_if_not_running(func):
    def func_wrapper(self):
        if not self.is_running:
            self.is_running = True
            return func(self)
    return func_wrapper

def only_if_running(func):
    def func_wrapper(self):
        if self.is_running:
            self.is_running = False
            return func(self)
    return func_wrapper

class Automator(object):
    def __init__(self, name = "base_automator", provider=None, gui=None, max_choice_limit: int = 0):
        self.name = name
        self.is_running = False
        self.provider = provider
        self.gui = gui
        self.max_choice_limit = max_choice_limit
        self.num_choices = 0
    
    @only_if_not_running
    def start(self):
        self.running_thread = threading.Thread(target=self.choose)
        self.running_thread.daemon = True
        self.running_thread.start()

    @only_if_running
    def stop(self):
         pass

    def choose(self):
        while self.is_running:
            print("automator deamon running")
            time.sleep(1)

    def toggle_start_stop(self):
        if not self.is_running:
            self.start()
        else:
            self.stop()
    
    def update_max_choice_limit(self, increment):
        self.max_choice_limit  += increment
        if self.max_choice_limit < 0: 
            self.max_choice_limit = 0 

        if self.gui:
                self.gui.update_selected_automator_text(self)


class RandomAutomator(Automator):
    def __init__(self, name = "Random Automator"):
        super().__init__(name = name)
        self.max_choice_limit = 6
    
    def choose(self):
        while self.is_running and self.max_choice_limit == 0 or self.num_choices < self.max_choice_limit:
            print("deamon running")
            time.sleep(1)
            self.num_choices +=1

            if self.gui:
                self.gui.update_selected_automator_text(self)
        else:
            self.stop()
            if self.gui:
                self.gui.update_selected_automator_text(self)



