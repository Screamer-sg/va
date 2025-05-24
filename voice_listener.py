import threading
import speech_recognition as sr
from assistant_state import assistant_should_stop_speaking

def listen_for_user_speech(timeout=0.8):
    global assistant_should_stop_speaking
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=2)
            # Якщо користувач почав говорити — зупиняємо асистента
            assistant_should_stop_speaking = True
        except sr.WaitTimeoutError:
            pass  # користувач не почав говорити