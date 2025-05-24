from odf.opendocument import OpenDocumentText
from odf.text import P, Span
from odf.style import Style, TextProperties
import os

def parse_formatting_from_command(text):
    """
    Витягує форматування з голосової команди (жирний, курсив, підкреслений).
    Повертає dict: {"bold": True/False, "italic": True/False, "underline": True/False}
    """
    fmt = {}
    if "жирн" in text or "bold" in text:
        fmt["bold"] = True
    if "курсив" in text or "italic" in text:
        fmt["italic"] = True
    if "підкреслен" in text or "underline" in text:
        fmt["underline"] = True
    return fmt

def append_text_to_odt(filename, text, formatting=None):
    """
    Додає текст у кінець ODT-документа з форматуванням.
    formatting: dict з ключами "bold", "italic", "underline".
    """
    if not os.path.exists(filename):
        return "Файл не знайдено!"

    # Відкриваємо документ
    try:
        doc = OpenDocumentText(filename=filename)
    except Exception as e:
        return f"Не вдалося відкрити документ: {e}"

    # Додаємо стиль, якщо потрібно
    style_name = None
    if formatting:
        style = Style(name="userstyle", family="text")
        if formatting.get("bold"):
            style.addElement(TextProperties(fontweight="bold"))
        if formatting.get("italic"):
            style.addElement(TextProperties(fontstyle="italic"))
        if formatting.get("underline"):
            style.addElement(TextProperties(textunderline="single"))
        doc.styles.addElement(style)
        style_name = "userstyle"

    # Додаємо новий абзац
    if style_name:
        span = Span(stylename=style_name, text=text)
        p = P()
        p.addElement(span)
    else:
        p = P(text=text)
    doc.text.addElement(p)

    # Зберігаємо
    try:
        doc.save(filename)
        return "Текст додано до документа."
    except Exception as e:
        return f"Не вдалося зберегти документ: {e}"