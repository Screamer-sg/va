import os
import tempfile
import time
import subprocess
import speech_recognition as sr
from settings import voice_settings
from assistant_state import assistant_should_stop_speaking

def listen_for_wake_word(wake_words=None, lang="uk-UA"):
    if wake_words is None:
        wake_words = ["асистент"]
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Слухаю для активації...")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            text = recognizer.recognize_google(audio, language=lang).lower()
            print(f"Розпізнано: {text}")
            for word in wake_words:
                if word in text:
                    return True
        except Exception:
            pass
    return False

def speak_text(text):
    global assistant_should_stop_speaking
    assistant_should_stop_speaking = False
    voice = getattr(voice_settings, "rhvoice_voice", "natalia")
    rate = float(getattr(voice_settings, "rhvoice_rate", 0))
    if rate < -1:
        rate = -1
    if rate > 1:
        rate = 1
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
        wav_path = fp.name
    cmd = [
        "RHVoice-client",
        "-s", voice,
        "-r", str(rate)
    ]
    try:
        proc = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(wav_path, "wb") as f:
            f.write(proc.stdout)
        # Відтворення у окремому процесі, щоб можна було зупинити
        play_proc = subprocess.Popen(["aplay", wav_path])
        while play_proc.poll() is None:
            if callable(assistant_should_stop_speaking) and assistant_should_stop_speaking():
                play_proc.terminate()
                break
            elif isinstance(assistant_should_stop_speaking, bool) and assistant_should_stop_speaking:
                play_proc.terminate()
                break
            time.sleep(0.1)
        play_proc.wait()
    except Exception as e:
        print("RHVoice error:", e)
        if hasattr(e, "stderr"):
            print(e.stderr.decode(errors="ignore"))
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

def recognize_speech_from_mic(lang="uk-UA"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio, language=lang)
    except Exception:
        return ""
