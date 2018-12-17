import tkinter as tk

class GUI(object):
    def __init__(self,root, settings):

        root.title('Swaipe')
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.provider_label = tk.Label(self.frame, text="Selected: Badoo")
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

        overall_label_text = f"Overall: [No: '{settings.no_overall_shortcut}'] [Yes: '{settings.yes_overall_shortcut}'] "
        overall_label = tk.Label(self.frame, text=overall_label_text)
        overall_label.grid(row=4, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)

        root.wm_attributes("-topmost", 1)
    
    def update_selected_provider_text(self, provider_name):
        self.provider_label = tk.Label(self.frame, text=f"Selected: {provider_name}")
        self.provider_label.grid(row=0, column=0, padx=5, pady=5, ipadx=10, sticky=tk.W)
