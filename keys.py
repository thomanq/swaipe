
from pynput.keyboard import KeyCode, Key, Listener

def key_to_string(key):
    '''Map key codes with ther string name:
    
        key_to_string(Key.alt) --> "alt" 
        
    '''

    keys = {Key.alt: "alt", Key.alt_l: "alt_l", Key.alt_r: "alt_r", Key.alt_gr: "alt_gr", Key.backspace: "backspace", Key.caps_lock: "caps_lock", Key.cmd: "cmd", Key.cmd_l: "cmd_l", Key.cmd_r: "cmd_r", Key.ctrl: "ctrl", Key.ctrl_l: "ctrl_l", Key.ctrl_r: "ctrl_r", Key.delete: "delete", Key.down: "down", Key.end: "end", Key.enter: "enter", Key.esc: "esc", Key.f1: "f1", Key.f2: "f2", Key.f3: "f3", Key.f4: "f4", Key.f5: "f5", Key.f6: "f6", Key.f7: "f7", Key.f8: "f8", Key.f9: "f9", Key.f10: "f10", Key.f11: "f11", Key.f12: "f12", Key.f13: "f13", Key.f14: "f14", Key.f15: "f15", Key.f16: "f16", Key.f17: "f17", Key.f18: "f18", Key.f19: "f19", Key.f20: "f20", Key.home: "home", Key.left: "left", Key.page_down: "page_down", Key.page_up: "page_up", Key.right: "right", Key.shift: "shift", Key.shift_l: "shift_l", Key.shift_r: "shift_r", Key.space: "space", Key.tab: "tab", Key.up: "up", Key.insert: "insert", Key.menu: "menu", Key.num_lock: "num_lock", Key.pause: "pause", Key.print_screen: "print_screen", Key.scroll_lock: "scroll_lock"}

    if key in keys: 
        return keys[key]    
    else:
        return None

def sc_base(shortcut):
    '''Get shortcut base:
    
        sc_base("shift+right") --> "right" 

    '''

    if shortcut == "+" or (len(shortcut) > 1 and shortcut[-1] == "+"):
        return "+"
    elif len(shortcut.split("+")) == 2:
        return shortcut.split("+")[1] 
    else:
        return shortcut

def sc_modifier(shortcut: str):
    '''Get shortcut modifier: 
            
        sc_modifier("shift+right") --> ["shift", "shift_l", "shift_r"]
        
    '''

    if len(shortcut.split("+")) == 2:
        return extend_modifier(shortcut.split("+")[0])
    else: 
        return [None]

def extend_modifier(shortcut: str):
    '''Help match left and right modifiers with main modifier name:

        extend_modifier("shift") --> ["shift", "shift_l", "shift_r"]
    
    '''

    if shortcut in ("alt", "cmd", "ctrl", "shift"):
        return [shortcut, shortcut + "_l", shortcut + "_r"]
    else:
        return [shortcut]

def is_modifier(key) -> bool:

    return key in (Key.alt, Key.alt_l, Key.alt_r, Key.alt_gr, Key.cmd, Key.cmd_l, Key.cmd_r, Key.ctrl, Key.ctrl_l, Key.ctrl_r, Key.shift, Key.shift_l, Key.shift_r)

def is_setting_shortcut(key, modifier, setting_shortcut: str) -> bool:
    '''Help match key and modifier with setting shortcut string:

        is_setting_shortcut(b, Key.shift_l, "shift+b") --> True
        is_setting_shortcut(b, None, "shift+b") --> False
    
    '''

    return key_to_string(modifier) in sc_modifier(setting_shortcut) \
       and (key_to_string(key) == sc_base(setting_shortcut) \
        or key == KeyCode.from_char(sc_base(setting_shortcut)))