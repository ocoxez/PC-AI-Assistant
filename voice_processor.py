import speech_recognition as sr
import pyttsx3
import threading

class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        try:
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'russian' in voice.name.lower() or 'russian' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except:
            pass
        
        self.tts_engine.setProperty('rate', 150)
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Ошибка калибровки микрофона: {e}")
    
    def listen(self):
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            return text.strip()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Речь не распознана")
            return None
        except Exception as e:
            print(f"Ошибка распознавания: {e}")
            return None
    
    def speak(self, text):
        def _speak():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Ошибка синтеза речи: {e}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()