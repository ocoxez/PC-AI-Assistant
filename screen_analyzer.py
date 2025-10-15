import pyautogui
import time
import os
import platform
import psutil

class ScreenAnalyzer:
    def __init__(self):
        self.screenshot_dir = "screenshots"
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def get_screen_context(self):
        try:
            screen_size = pyautogui.size()
            mouse_position = pyautogui.position()
            
            running_apps = self._get_running_applications()
            
            system_info = self._get_system_info()
            
            context = f"""
ЭКРАН:
- Разрешение: {screen_size}
- Позиция курсора: {mouse_position}
- Система: {system_info}

ЗАПУЩЕННЫЕ ПРИЛОЖЕНИЯ:
{running_apps}
"""
            return context
        except Exception as e:
            return f"Ошибка анализа экрана: {str(e)}"
    
    def _get_running_applications(self):
        try:
            apps = []
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if self._is_user_application(proc.info['name']):
                        apps.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            unique_apps = list(set(apps))[:10]
            return ", ".join(unique_apps) if unique_apps else "Не обнаружено"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def _is_user_application(self, process_name):
        system_processes = {
            'svchost.exe', 'explorer.exe', 'winlogon.exe', 'csrss.exe', 
            'services.exe', 'lsass.exe', 'smss.exe', 'System', 'System Idle Process',
            'taskhost.exe', 'dwm.exe', 'fontdrvhost.exe'
        }
        
        user_apps = {
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe', 
            'notepad.exe', 'calc.exe', 'word.exe', 'excel.exe', 'powerpnt.exe',
            'code.exe', 'pycharm.exe', 'devenv.exe', 'photoshop.exe',
            'steam.exe', 'discord.exe', 'telegram.exe', 'spotify.exe',
            'vlc.exe', 'winword.exe', 'excel.exe', 'outlook.exe'
        }
        
        process_lower = process_name.lower()
        return (process_lower in user_apps or 
                (process_lower.endswith('.exe') and process_lower not in system_processes))
    
    def _get_system_info(self):
        try:
            system = platform.system()
            version = platform.version()
            
            memory = psutil.virtual_memory()
            memory_usage = f"{memory.percent}%"
            
            cpu_usage = f"{psutil.cpu_percent(interval=1)}%"
            
            return f"{system} {version}, CPU: {cpu_usage}, RAM: {memory_usage}"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def take_screenshot(self):
        try:
            timestamp = int(time.time())
            filename = f"{self.screenshot_dir}/screenshot_{timestamp}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return filename
        except Exception as e:
            print(f"Ошибка скриншота: {e}")
            return None
    
    def get_detailed_screen_analysis(self):
        try:
            detailed_info = f"""
ДЕТАЛЬНЫЙ АНАЛИЗ СИСТЕМЫ:
- Время работы системы: {self._get_system_uptime()}
- Дисковое пространство: {self._get_disk_usage()}
"""
            return detailed_info
        except Exception as e:
            return f"Ошибка детального анализа: {str(e)}"
    
    def _get_system_uptime(self):
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
        except:
            return "Не доступно"
    
    def _get_disk_usage(self):
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free // (1024**3)
            total_gb = disk.total // (1024**3)
            return f"{free_gb}Гб свободно из {total_gb}Гб"
        except:
            return "Не доступно"