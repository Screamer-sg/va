import subprocess
import time
import speech_recognition as sr
from allowed_programs import allowed_programs

notepad_programs = set(allowed_programs.keys())

def is_notepad_open(prog_key):
    from allowed_programs import allowed_programs
    prog = allowed_programs.get(prog_key)
    if not prog:
        return False
    try:
        out = subprocess.check_output(
            ["xdotool", "search", "--class", prog], encoding="utf-8", stderr=subprocess.DEVNULL
        )
        window_ids = out.splitlines()
        return bool(window_ids)
    except Exception:
        return False

def open_notepad(prog_key):
    prog = allowed_programs.get(prog_key)
    if not prog:
        raise ValueError(f"Програма '{prog_key}' не дозволена!")
    subprocess.Popen([prog])
    time.sleep(1.5)

def focus_notepad_window(notepad_key):
    prog = allowed_programs.get(notepad_key)
    if not prog:
        print(f"Блокнот {notepad_key} не знайдено.")
        return False
    try:
        window_search = subprocess.check_output(
            ["xdotool", "search", "--class", prog], encoding="utf-8"
        )
        window_id = window_search.splitlines()[0]
        subprocess.call(["xdotool", "windowactivate", "--sync", window_id])
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"Не вдалося знайти або сфокусувати {prog}: {e}")
        return False

def type_text_to_notepad(text, notepad_key):
    if focus_notepad_window(notepad_key):
        subprocess.call(["xdotool", "type", "--delay", "10", text])

def recognize_speech_from_mic_for_notepad(lang="uk-UA"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Говоріть...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language=lang)
        print("Розпізнано:", text)
        return text
    except Exception as e:
        print("Не вдалося розпізнати:", e)
        return ""
