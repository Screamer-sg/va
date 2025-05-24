import requests
import base64

GEMINI_API_KEY = ""  # Вставте свій ключ від Gemini API!

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {"Content-Type": "application/json"}

def gemini_ask(prompt, lang="uk", temperature=0.7):
    """
    Задає довільне питання до Gemini (як до GPT).
    """
    data = {
        "contents": [{
            "parts": [
                {"text": f"{prompt}\nВідповідай мовою: {lang}."}
            ]
        }],
        "generationConfig": {
            "temperature": temperature
        }
    }
    params = {"key": GEMINI_API_KEY}
    try:
        response = requests.post(GEMINI_API_URL, headers=HEADERS, json=data, params=params, timeout=30)
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            return f"Помилка Gemini (код {response.status_code}): {response.text}"
    except Exception as e:
        return f"Не вдалося звернутися до Gemini: {e}"

def gemini_search(query, lang="uk"):
    """
    Пошук в інтернеті через Gemini (використовує prompt-інструкцію).
    """
    search_prompt = (
        f"Виконай короткий пошук в інтернеті за запитом: '{query}'. "
        f"Відповідь дай мовою: {lang}. Додай посилання на 1-3 джерела, якщо можливо."
    )
    return gemini_ask(search_prompt, lang=lang)

def gemini_translate(text, target_lang="en"):
    """
    Переклад тексту через Gemini.
    """
    prompt = (
        f"Переклади цей текст на {target_lang} (тільки переклад, без коментарів):\n{text}"
    )
    return gemini_ask(prompt, lang=target_lang)

def gemini_multimodal(image_bytes, prompt, lang="uk"):
    """
    Аналіз або генерація опису для зображення через Gemini Vision.
    image_bytes — байти зображення (JPEG/PNG).
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
    image_b64 = base64.b64encode(image_bytes).decode()
    data = {
        "contents": [{
            "parts": [
                {
                    "text": f"{prompt}\nВідповідь дай мовою: {lang}."
                },
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": image_b64
                    }
                }
            ]
        }]
    }
    params = {"key": GEMINI_API_KEY}
    try:
        response = requests.post(url, headers=HEADERS, json=data, params=params, timeout=30)
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        else:
            return f"Помилка Gemini (код {response.status_code}): {response.text}"
    except Exception as e:
        return f"Не вдалося звернутися до Gemini Vision: {e}"

def gemini_detect_language(text):
    """
    Автоматичне визначення мови тексту через Gemini.
    """
    prompt = (
        "Визнач мову цього тексту. Відповідь тільки у вигляді коду ISO (наприклад, uk, en, pl, de):\n" + text
    )
    return gemini_ask(prompt, lang="en", temperature=0).strip().split()[0]
