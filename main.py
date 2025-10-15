import threading
import time
import requests
import json
import re
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
        self.api_key = config.OPENROUTER_API_KEY
        
    def start(self):
        print("ИИ ассистент запущен")
        
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
            screen_context, clipboard_text = self._get_context_for_query(user_input)
            
            full_context = screen_context
            if clipboard_text:
                if len(clipboard_text) > 2000:
                    clipboard_text = clipboard_text[:2000] + "... [текст обрезан]"
                full_context += f"\n\nСКОПИРОВАННЫЙ ТЕКСТ ({len(clipboard_text)} символов): {clipboard_text}"

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "PC AI Assistant",
                },
                data=json.dumps({
                    "model": "tngtech/deepseek-r1t2-chimera:free",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Ты - интеллектуальный ассистент для ПК. У тебя есть доступ к информации о системе и скопированному тексту.\n\nКОНТЕКСТ СИСТЕМЫ:\n{full_context}\n\nОтвечай кратко и по делу. Если есть скопированный текст - работай с ним."
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._extract_response(result)
            else:
                print(f"Ошибка API: {response.status_code}")
                return "Извините, произошла ошибка при обращении к ИИ"
                
        except requests.exceptions.Timeout:
            return "Таймаут подключения к ИИ"
        except Exception as e:
            print(f"Ошибка соединения: {str(e)}")
            return "Извините, произошла ошибка при подключении"
    
    def _get_context_for_query(self, user_input):
        user_input_lower = user_input.lower()
        
        basic_context = self.screen_analyzer.get_screen_context()
        
        clipboard_text = ""
        
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
            else:
                print("В буфере обмена нет текста")
        
        if any(word in user_input_lower for word in [
            'систем', 'памят', 'процессор', 'cpu', 'ram', 'диск', 'батаре', 
            'монитор', 'подробн', 'деталь', 'анализ', 'информац', 'состояние'
        ]):
            detailed_context = self.screen_analyzer.get_detailed_screen_analysis()
            return f"{basic_context}\n{detailed_context}", clipboard_text
        
        return basic_context, clipboard_text
    
    def _extract_response(self, api_result):
        try:
            if 'choices' not in api_result or not api_result['choices']:
                return "Нет ответа от модели"
            
            choice = api_result['choices'][0]
            message = choice.get('message', {})
            
            content = message.get('content', '').strip()
            if content:
                return self._clean_response(content)
            
            reasoning = message.get('reasoning', '').strip()
            if reasoning:
                return self._extract_from_reasoning(reasoning)
            
            return "Не удалось извлечь ответ от ИИ"
            
        except Exception as e:
            return f"Ошибка обработки ответа: {str(e)}"
    
    def _extract_from_reasoning(self, reasoning_text):
        cleaned = self._clean_response(reasoning_text)
        
        sentences = re.split(r'[.!?]+', cleaned)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 1:
            answer = '. '.join(sentences[-2:]) + '.'
            return answer
        else:
            return cleaned
    
    def _clean_response(self, text):
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if len(text) > 400:
            text = text[:400] + '...'
        return text
    
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

        