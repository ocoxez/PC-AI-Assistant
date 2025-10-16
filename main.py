import threading
import time
import base64
import io
from PIL import Image
from openai import OpenAI
from voice_processor import VoiceProcessor
from screen_analyzer import ScreenAnalyzer
from input_controller import InputController
import config

class AIAssistant:
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.screen_analyzer = ScreenAnalyzer()
        self.input_controller = InputController()
        self.is_listening = False
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
        )
        
    def start(self):
        print("ИИ ассистент запущен")
        print("Модель: Mistral Small 3.2")
        print("Говорите команды...")
        print("Ключевые слова для скриншота: экран, видишь, посмотри, покажи")
        
        self.is_listening = True
        listen_thread = threading.Thread(target=self._listen_loop)
        listen_thread.daemon = True
        listen_thread.start()
        
    def _listen_loop(self):
        while self.is_listening:
            try:
                text = self.voice_processor.listen()
                if text:
                    self._process_command(text)
            except Exception as e:
                print(f"Ошибка в цикле прослушивания: {e}")
                time.sleep(1)
    
    def _process_command(self, text):
        print(f"Распознано: {text}")
        
        if self._execute_local_commands(text):
            return
            
        response = self._get_ai_response(text)
        
        if response:
            print(f"Ответ: {response}")
            self.voice_processor.speak(response)
    
    def _execute_local_commands(self, text):
        command = text.lower().strip()
        
        if any(word in command for word in ['открой калькулятор', 'калькулятор']):
            print("Открываю калькулятор")
            self.input_controller.open_calculator()
            self.voice_processor.speak("Открываю калькулятор")
            return True
            
        elif any(word in command for word in ['открой браузер', 'браузер']):
            print("Открываю браузер")
            self.input_controller.open_browser()
            self.voice_processor.speak("Открываю браузер")
            return True
            
        elif any(word in command for word in ['открой блокнот', 'блокнот']):
            print("Открываю блокнот")
            self.input_controller.open_notepad()
            self.voice_processor.speak("Открываю блокнот")
            return True
            
        elif any(word in command for word in ['открой проводник', 'проводник']):
            print("Открываю проводник")
            self.input_controller.open_explorer()
            self.voice_processor.speak("Открываю проводник")
            return True
            
        elif any(word in command for word in ['скриншот', 'снимок экрана']):
            print("Делаю скриншот")
            filename = self.screen_analyzer.take_screenshot()
            self.voice_processor.speak("Скриншот сохранен")
            print(f"Скриншот сохранен: {filename}")
            return True
            
        elif any(word in command for word in ['время', 'который час', 'текущее время']):
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            response = f"Сейчас {current_time}"
            print(f"Время: {response}")
            self.voice_processor.speak(response)
            return True
            
        elif any(word in command for word in ['дата', 'какое число', 'какая дата']):
            import datetime
            current_date = datetime.datetime.now().strftime("%d.%m.%Y")
            response = f"Сегодня {current_date}"
            print(f"Дата: {response}")
            self.voice_processor.speak(response)
            return True
            
        elif any(word in command for word in ['остановись', 'стоп', 'выход']):
            self.stop()
            return True
            
        return False
    
    def _get_ai_response(self, user_input):
        try:
            screen_context, clipboard_text, needs_screenshot = self._get_context_for_query(user_input)
            
            if needs_screenshot:
                print("Создаю скриншот для анализа...")
                screenshot_data = self._take_screenshot_base64()
                
                if screenshot_data:
                    self.voice_processor.speak("Анализирую экран")
                    
                    completion = self.client.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "http://localhost:3000",
                            "X-Title": "PC AI Assistant",
                        },
                        extra_body={},
                        model="mistralai/mistral-small-3.2-24b-instruct:free",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"""Ты - интеллектуальный ассистент для ПК. Проанализируй скриншот экрана и ответь на вопрос пользователя.

КОНТЕКСТ СИСТЕМЫ:
{screen_context}

{"СКОПИРОВАННЫЙ ТЕКСТ: " + clipboard_text if clipboard_text else ""}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_input}

Опиши что видишь на экране и ответь на вопрос пользователя."""
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{screenshot_data}"
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=800,
                        temperature=0.7
                    )
                    
                    return completion.choices[0].message.content
                else:
                    return "Не удалось создать скриншот для анализа"
            else:
                prompt = f"""Ты - интеллектуальный ассистент для ПК. Отвечай кратко и по делу.

КОНТЕКСТ СИСТЕМЫ:
{screen_context}

{"СКОПИРОВАННЫЙ ТЕКСТ: " + clipboard_text if clipboard_text else ""}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_input}"""

                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "PC AI Assistant",
                    },
                    extra_body={},
                    model="mistralai/mistral-small-3.2-24b-instruct:free",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Ошибка при обращении к ИИ: {str(e)}")
            return "Извините, произошла ошибка при подключении к ИИ"
    
    def _take_screenshot_base64(self):
        """Создание скриншота и кодирование в base64"""
        try:
            import pyautogui
            from PIL import Image
            import io
            import base64
            
            screenshot = pyautogui.screenshot()
            
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG", optimize=True, quality=85)
            screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            print(f"Скриншот создан и закодирован: {len(screenshot_base64)} символов")
            return screenshot_base64
            
        except Exception as e:
            print(f"Ошибка создания скриншота: {e}")
            return None
    
    def _get_context_for_query(self, user_input):
        user_input_lower = user_input.lower()
        
        basic_context = self.screen_analyzer.get_screen_context()
        
        clipboard_text = ""
        needs_screenshot = False
        
        screenshot_keywords = [
            'экран', 'экране', 'видишь', 'посмотри', 'покажи', 'что на экране',
            'что сейчас на экране', 'что видно', 'анализируй экран', 'осмотри'
        ]
        
        if any(keyword in user_input_lower for keyword in screenshot_keywords):
            needs_screenshot = True
            print("Обнаружены ключевые слова для скриншота")
        
        text_keywords = [
            'текст', 'переведи', 'анализируй', 'объясни', 'суммируй', 'рерайт',
            'перефразируй', 'коротко', 'скопирован', 'прочитай', 'напиши',
            'составь', 'перескажи', 'озвучь', 'произнеси', 'это', 'этом'
        ]
        
        if any(keyword in user_input_lower for keyword in text_keywords):
            print("Проверяю буфер обмена на наличие текста")
            clipboard_text = self.input_controller.get_clipboard_text()
            
            if clipboard_text:
                print(f"Обнаружен текст в буфере обмена: {clipboard_text[:100]}...")
                if len(clipboard_text) > 3000:
                    clipboard_text = clipboard_text[:3000] + "... [текст обрезан]"
            else:
                print("В буфере обмена нет текста")
        
        if any(word in user_input_lower for word in [
            'систем', 'памят', 'процессор', 'cpu', 'ram', 'диск', 'батаре', 
            'монитор', 'подробн', 'деталь', 'анализ', 'информац', 'состояние'
        ]):
            detailed_context = self.screen_analyzer.get_detailed_screen_analysis()
            return f"{basic_context}\n{detailed_context}", clipboard_text, needs_screenshot
        
        return basic_context, clipboard_text, needs_screenshot
    
    def stop(self):
        self.is_listening = False
        print("Останавливаю ассистента")
        self.voice_processor.speak("Ассистент останавливается")
        print("Ассистент остановлен")

if __name__ == "__main__":
    assistant = AIAssistant()
    try:
        assistant.start()
        print("Ассистент работает в фоновом режиме")
        print("Для выхода нажмите Ctrl+C или скажите 'стоп'")
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Прерывание с клавиатуры")
        assistant.stop()