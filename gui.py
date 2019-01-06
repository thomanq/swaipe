import tkinter as tk

class GUI(object):
    def __init__(self,root, settings):

        self.root = root
        self.root.title('Swaipe')
        self.root.geometry("430x230")
        self.frame = tk.Frame(self.root)
        self.frame.pack_propagate(0)
        self.frame.pack(fill=tk.BOTH, expand=1) 

        self.provider_label = tk.Label(self.frame, text="Selected:")
        self.provider_label.grid(row=0, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        badoo_label_text = f"Badoo:  [Select: '{settings.select_badoo_provider}'] [Open: '{settings.go_to_badoo}']"
        badoo_label = tk.Label(self.frame, text=badoo_label_text)
        badoo_label.grid(row=1, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        tinder_label_text = f"Tinder:  [Select: '{settings.select_tinder_provider}'] [Open: '{settings.go_to_tinder}']"
        tinder_label = tk.Label(self.frame, text=tinder_label_text)
        tinder_label.grid(row=2, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        picture_label_text = f"Picture:  [No: '{settings.no_pic_shortcut}'] [Yes: '{settings.yes_pic_shortcut}']"
        picture_label = tk.Label(self.frame, text=picture_label_text)
        picture_label.grid(row=3, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        profile_label_text = f"Profile: [No: '{settings.no_profile_shortcut}'] [Yes: '{settings.yes_profile_shortcut}'] "
        profile_label = tk.Label(self.frame, text=profile_label_text)
        profile_label.grid(row=4, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        automator_start_stop_label_text = f"Automator: [Start/stop: '{settings.start_stop_automator}'] [Next/previous: '{settings.choose_next_automator}'/'{settings.choose_previous_automator}'] "
        automator_start_stop_label = tk.Label(self.frame, text=automator_start_stop_label_text)
        automator_start_stop_label.grid(row=5, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        self.current_automator_label = tk.Label(self.frame, text="Selected:")
        self.current_automator_label.grid(row=6, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        self.root.wm_attributes("-topmost", 1)
    
    def update_selected_provider_text(self, provider_name):
        self.provider_label.destroy()
        self.provider_label = tk.Label(self.frame, text=f"Selected: {provider_name}")
        self.provider_label.grid(row=0, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

    def update_selected_automator_text(self, automator):
        self.current_automator_label.destroy()
        automator_name =  f"{automator.name} ({int(automator.yes_rate_goal*100)}%)" if automator.yes_rate_goal !=0 else automator.name
        status_text = "Started" if automator.is_running else "Stopped"
        max_text = "∞" if automator.max_choice_limit == 0 else str(automator.max_choice_limit)
        yes_rate = f"(currently: {round(automator.yes_rate * 100, 1)}%)" if automator.yes_rate != 0 else ""
        self.current_automator_label = tk.Label(self.frame, text=f"Selected: {automator_name} ({status_text}) ({automator.num_choices}/{max_text}) {yes_rate}")
        self.current_automator_label.grid(row=6, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

    def hide(self):
        self.root.attributes('-alpha', 0.0)
        
    def show(self):
        self.root.attributes('-alpha', 1.0)
