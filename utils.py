import datetime

def get_current_timestamp():
    """
    Повертає поточну дату і час у форматі YYYY-MM-DD HH:MM:SS.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def normalize_text(text):
    """
    Очищає текст: прибирає зайві пробіли, переводить у нижній регістр.
    """
    return " ".join(text.lower().split())

def parse_numbers_from_text(text):
    """
    Повертає список чисел, знайдених у тексті.
    """
    import re
    return [int(n) for n in re.findall(r"\d+", text)]