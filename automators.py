import time
import datetime
import threading
import random

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

def repeat(func):
    '''
        Repeats function until max_choice_limit has been reached then stops.
        If max_choice_limit == 0, repeats indefinitely.

        Throttles repeat rate (max 1 call every min_choice_interval seconds).

    '''

    def func_wrapper(self):          
        while self.is_running and (self.max_choice_limit == 0 or self.num_choices < self.max_choice_limit):
            now = datetime.datetime.now()
            
            func(self)
            self.num_choices +=1
            self.update_yes_rate()

            delta = datetime.datetime.now() - now
            delta_seconds = delta.seconds + delta.microseconds / 1_000_000
            if delta_seconds < self.min_choice_interval:
                seconds_until_min = self.min_choice_interval - delta_seconds
                time.sleep(seconds_until_min + random.uniform(0, self.max_choice_interval - self.min_choice_interval))

        else:
            self.stop()
            return
    return func_wrapper

class Automator(object):
    def __init__(self, name = "base_automator", provider=None, max_choice_limit: int = 0, min_choice_interval: float=2.5, 
         max_choice_interval: float=4.5, yes_rate_goal: float = 0.0):
        self.name = name
        self.is_running = False
        self.provider = provider
        self.max_choice_limit = max_choice_limit
        self.num_choices = 0
        self.min_choice_interval = min_choice_interval
        self.max_choice_interval = max_choice_interval
        self.num_yesses = 0
        self.yes_rate = 0
        self.yes_rate_goal = yes_rate_goal
    
    @only_if_not_running
    def start(self):
        self.running_thread = threading.Thread(target=self.choose)
        self.running_thread.daemon = True
        self.running_thread.start()

    @only_if_running
    def stop(self):
         pass

    @repeat
    def choose(self):
        print("automator deamon running")

    def toggle_start_stop(self):
        if not self.is_running:
            self.start()
        else:
            self.stop()
    
    def update_max_choice_limit(self, increment):
        self.max_choice_limit  += increment
        if self.max_choice_limit < 0: 
            self.max_choice_limit = 0 
    
    def update_yes_rate(self):
        self.yes_rate = self.num_yesses / self.num_choices if self.num_choices != 0 else 0

    def update_yes_rate_goal(self, increment):
        self.yes_rate_goal += increment

    def set_provider(self, provider):
        if provider != self.provider:
            self.num_choices = 0
            self.num_yesses = 0
            self.yes_rate = 0
            self.provider = provider

class RandomAutomator(Automator):
    def __init__(self, name = "Random Automator", max_choice_limit = 0, min_choice_interval: float=1.9, max_choice_interval: float=5.1, yes_rate_goal: float = 0.65):
        super().__init__(name=name, max_choice_limit=max_choice_limit, min_choice_interval=min_choice_interval,max_choice_interval=max_choice_interval, yes_rate_goal=yes_rate_goal)
    
    @repeat
    def choose(self):
        if self.provider:
            if self.yes_rate <= self.yes_rate_goal:
                self.provider.handle_yes_no_profile(True)
                self.num_yesses += 1
            else:
                self.provider.handle_yes_no_profile(False)
                
