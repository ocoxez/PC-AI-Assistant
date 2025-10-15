import pyautogui
import subprocess
import time
import os
import pyperclip

class InputController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def open_calculator(self):
        try:
            if os.name == 'nt':
                subprocess.Popen('calc.exe')
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка открытия калькулятора: {e}")
            return False
    
    def open_browser(self):
        try:
            if os.name == 'nt':
                subprocess.Popen('start chrome', shell=True)
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка открытия браузера: {e}")
            return False
    
    def open_notepad(self):
        try:
            if os.name == 'nt':
                subprocess.Popen('notepad.exe')
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка открытия блокнота: {e}")
            return False
    
    def open_explorer(self):
        try:
            if os.name == 'nt':
                subprocess.Popen('explorer.exe')
                return True
            else:
                subprocess.Popen(['nautilus', 'dolphin', 'thunar'][0])
                return True
        except Exception as e:
            print(f"Ошибка открытия проводника: {e}")
            return False
    
    def get_clipboard_text(self):
        try:
            text = pyperclip.paste()
            
            if text and len(text.strip()) > 5:
                print(f"Текст из буфера обмена: {len(text)} символов")
                return text.strip()
            else:
                return ""
                
        except Exception as e:
            print(f"Ошибка чтения буфера обмена: {e}")
            return ""
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{int(time.time())}.png"
            screenshot.save(filename)
            return filename
        except Exception as e:
            print(f"Ошибка создания скриншота: {e}")
            return None