import os
import tempfile
import time
import subprocess
import logging
import speech_recognition as sr
from settings import voice_settings
from assistant_state import assistant_should_stop_speaking

logging.basicConfig(level=logging.INFO)

def listen_for_wake_word(wake_words=None, lang="uk-UA"):
    """
    Слухає мікрофон і повертає True, якщо розпізнано ключове слово для активації.
    """
    if wake_words is None:
        wake_words = ["асистент"]
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            logging.info("Слухаю для активації...")
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
            try:
                text = recognizer.recognize_google(audio, language=lang).lower()
                logging.info(f"Розпізнано: {text}")
                return any(word in text for word in wake_words)
            except sr.UnknownValueError:
                logging.warning("Не вдалося розпізнати мову.")
            except sr.RequestError as e:
                logging.error(f"Помилка доступу до Google API: {e}")
    except OSError as e:
        logging.error(f"Помилка доступу до мікрофона: {e}")
    except Exception as e:
        logging.error(f"Неочікувана помилка: {e}")
    return False

def speak_text(text):
    """
    Озвучує текст за допомогою RHVoice, із можливістю зупинити програвання.
    """
    global assistant_should_stop_speaking

    # Перевірка залежностей
    if not shutil.which("RHVoice-client"):
        logging.error("RHVoice-client не знайдено в системі.")
        return
    if not shutil.which("aplay"):
        logging.error("aplay не знайдено в системі.")
        return

    assistant_should_stop_speaking = False
    voice = getattr(voice_settings, "rhvoice_voice", "natalia")
    try:
        rate = float(getattr(voice_settings, "rhvoice_rate", 0))
        rate = min(max(rate, -1), 1)
    except Exception:
        rate = 0

    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            wav_path = fp.name

        cmd = [
            "RHVoice-client",
            "-s", voice,
            "-r", str(rate)
        ]
        proc = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(wav_path, "wb") as f:
            f.write(proc.stdout)

        play_proc = subprocess.Popen(["aplay", wav_path])
        while play_proc.poll() is None:
            stop = (callable(assistant_should_stop_speaking) and assistant_should_stop_speaking()) \
                or (isinstance(assistant_should_stop_speaking, bool) and assistant_should_stop_speaking)
            if stop:
                play_proc.terminate()
                break
            time.sleep(0.1)
        play_proc.wait()
    except subprocess.CalledProcessError as e:
        logging.error(f"RHVoice error: {e}")
        if hasattr(e, "stderr"):
            logging.error(e.stderr.decode(errors="ignore"))
    except Exception as e:
        logging.error(f"Помилка при синтезі або програванні мови: {e}")
    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception as e:
                logging.warning(f"Не вдалося видалити тимчасовий файл: {e}")

def recognize_speech_from_mic(lang="uk-UA"):
    """
    Розпізнає мовлення з мікрофона та повертає текст.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        return recognizer.recognize_google(audio, language=lang)
    except sr.UnknownValueError:
        logging.warning("Не вдалося розпізнати мову.")
    except sr.RequestError as e:
        logging.error(f"Помилка доступу до Google API: {e}")
    except OSError as e:
        logging.error(f"Помилка мікрофону: {e}")
    except Exception as e:
        logging.error(f"Неочікувана помилка: {e}")
    return ""

# Додатково: перевірка залежності shutil
import shutil