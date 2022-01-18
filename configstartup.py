from kivy.config import Config


"""
configstartup.py is used to set graphics 
 
"""
Config.set('kivy', 'window_icon','images/w.png')  # Windows uses a 64x64 png
Config.set('kivy', 'exit_on_escape', 0)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
#Config.set('kivy', 'log_level', 'error')

