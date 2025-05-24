import office_tools
import system_tools
import gemini_tools
import subprocess
from allowed_programs import allowed_programs
from speech_tools import speak_text
from voice_listener import listen_for_user_speech

# --- Додаємо імпорт з voice_notepad_linux ---
from voice_notepad_linux import is_notepad_open, open_notepad, type_text_to_notepad, notepad_programs

import threading
import re

def speak_with_interrupt(text):
    listener_thread = threading.Thread(target=listen_for_user_speech)
    listener_thread.start()
    speak_text(text)
    listener_thread.join()

def parse_office_command(user_text):
    text = user_text.lower()
    if ("додай у документ" in text or "add to document" in text) and ("текст" in text or "text" in text):
        try:
            doc_part = text.split("додай у документ")[-1].strip() if "додай у документ" in text else text.split("add to document")[-1].strip()
            if "текст:" in doc_part:
                doc_name, content = doc_part.split("текст:", 1)
                doc_name = doc_name.strip()
                content = content.strip()
                formatting = office_tools.parse_formatting_from_command(text)
                from file_tools import find_files
                files = find_files(directory=".", pattern=doc_name, ext=".odt")
                if not files:
                    return "Документ не знайдено для додавання тексту."
                result = office_tools.append_text_to_odt(files[0], content, formatting)
                return result
            else:
                return "Будь ласка, використовуйте формат: додай у документ <назва> текст: <текст> <форматування>"
        except Exception as e:
            return f"Помилка розбору команди: {e}"
    return None

def parse_system_command(user_text, last_response=None):
    text = user_text.lower()

    # --- Інтеграція з voice_notepad_linux ---
    # Відкрити блокнот з голосовим введенням
    launch_patterns = [
        r"(запусти|відкрий|стартуй|open|start)\s+(програму\s+)?(блокнот|\w+)(.*голос.*введення)?",
    ]
    for pattern in launch_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            prog_key = match.group(3).lower()
            if prog_key == "блокнот" and "блокнот" not in allowed_programs:
                prog_key = next(iter(allowed_programs))
            if prog_key in allowed_programs:
                try:
                    open_notepad(prog_key)
                    if match.group(4) and "голос" in match.group(4):
                        user_text_for_notepad = recognize_speech_from_mic_for_notepad()
                        if user_text_for_notepad:
                            type_text_to_notepad(user_text_for_notepad, prog_key)
                            return f"Блокнот відкрито. Ваш текст: {user_text_for_notepad}"
                        return "Блокнот відкрито, але текст не розпізнано."
                    return f"Відкриваю блокнот: {allowed_programs[prog_key]}"
                except Exception as e:
                    return f"Не вдалося відкрити блокнот '{allowed_programs[prog_key]}': {e}"
            else:
                return "Цей блокнот не дозволений або не знайдений у списку."

    # Перенести попередню відповідь у блокнот
    if re.search(r"(запиши|встав|перенеси|copy|write|insert).*(відповідь|answer)", text, re.IGNORECASE):
        for prog_key in notepad_programs:
            if prog_key in text or "блокнот" in text:
                if last_response:
                    if not is_notepad_open(prog_key):
                        open_notepad(prog_key)
                        import time
                        time.sleep(1.5)
                    type_text_to_notepad(last_response, prog_key)
                    return "Відповідь скопійовано у блокнот."
                else:
                    return "Немає попередньої відповіді для вставки."
        return "Не знайдено відповідний блокнот у команді."


    # --- Стандартний запуск програм ---
    launch_patterns_no_voice = [
        r"(запусти|відкрий|стартуй|open|start)\s+(програму\s+)?(\w+)",
    ]
    for pattern in launch_patterns_no_voice:
        match = re.search(pattern, text)
        if match:
            prog = match.group(3)
            prog_exec = allowed_programs.get(prog, prog)
            try:
                subprocess.Popen([prog_exec])
                return f"Відкриваю програму: {prog_exec}"
            except Exception as e:
                return f"Не вдалося відкрити програму '{prog_exec}': {e}"

    if "гучн" in text or "volume" in text:
        if "зроби тихіше" in text or "quieter" in text or "менше" in text:
            return system_tools.change_volume(-10)
        if "зроби гучніше" in text or "louder" in text or "більше" in text:
            return system_tools.change_volume(10)
        if "вимкни звук" in text or "mute" in text:
            return system_tools.mute_volume()
        if "увімкни звук" in text or "unmute" in text:
            return system_tools.unmute_volume()
        match = re.search(r"(гучність|volume)\s*(\d{1,3})", text)
        if match:
            level = int(match.group(2))
            return system_tools.set_volume(level)

    if "wi-fi" in text or "wifi" in text:
        if "увімкни" in text or "on" in text or "enable" in text:
            return system_tools.toggle_wifi(True)
        if "вимкни" in text or "off" in text or "disable" in text:
            return system_tools.toggle_wifi(False)

    if "bluetooth" in text:
        if "увімкни" in text or "on" in text or "enable" in text:
            return system_tools.toggle_bluetooth(True)
        if "вимкни" in text or "off" in text or "disable" in text:
            return system_tools.toggle_bluetooth(False)

    if "сплячий" in text or "sleep" in text:
        return system_tools.system_sleep()
    if "гібернація" in text or "hibernate" in text:
        return system_tools.system_hibernate()

    return None

def parse_gemini_command(user_text):
    text = user_text.lower()

    if "знайди в інтернеті" in text or "search the internet" in text:
        query = user_text.split("знайди в інтернеті", 1)[-1].strip() if "знайди в інтернеті" in text else user_text.split("search the internet", 1)[-1].strip()
        if not query:
            return "Будь ласка, уточни, що шукати."
        return gemini_tools.gemini_search(query)

    if "переклади" in text or "translate" in text:
        parts = user_text.split(":")
        if len(parts) >= 2:
            text_to_translate = parts[1].strip()
            if "англійською" in text or "english" in text:
                return gemini_tools.gemini_translate(text_to_translate, target_lang="en")
            elif "українською" in text or "ukrainian" in text:
                return gemini_tools.gemini_translate(text_to_translate, target_lang="uk")
            else:
                return gemini_tools.gemini_translate(text_to_translate, target_lang="en")
        else:
            return "Будь ласка, використай формат: 'переклади на англійську: Привіт!'"

    if "якою мовою" in text or "which language" in text:
        sample = user_text.split(":")[-1].strip()
        return gemini_tools.gemini_detect_language(sample)

    if "запитай у gemini" in text or "ask gemini" in text:
        prompt = user_text.split("запитай у gemini", 1)[-1].strip() if "запитай у gemini" in text else user_text.split("ask gemini", 1)[-1].strip()
        if not prompt:
            return "Яке питання поставити Gemini?"
        return gemini_tools.gemini_ask(prompt)

    return None

def generate_response(user_text, lang="uk", last_response=None):
    # Пріоритет парсерів: системні → офісні → інтернет (Gemini)
    sys_cmd = parse_system_command(user_text, last_response=last_response)
    if sys_cmd:
        return sys_cmd

    off_cmd = parse_office_command(user_text)
    if off_cmd:
        return off_cmd

    gemini_cmd = parse_gemini_command(user_text)
    if gemini_cmd:
        return gemini_cmd

    # Якщо не розпізнано — надсилати як довільний запит до Gemini
    return gemini_tools.gemini_ask(user_text, lang=lang)
