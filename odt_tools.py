from odf.opendocument import OpenDocumentText
from odf.text import P
import os

def create_odt(filename, title=None):
    doc = OpenDocumentText()
    if title:
        p = P(text=title)
        doc.text.addElement(p)
    doc.save(filename)
    return f"Файл {filename} створено."

def read_odt(filename):
    if not os.path.exists(filename):
        return "Файл не знайдено!"
    try:
        doc = OpenDocumentText(filename=filename)
        paras = [str(p) for p in doc.getElementsByType(P)]
        import re
        clean_paras = [re.sub(r'<[^>]+>', '', p) for p in paras]
        return "\n".join(clean_paras)
    except Exception as e:
        return f"Помилка читання ODT: {e}"

def replace_text_in_odt(filename, old_text, new_text):
    if not os.path.exists(filename):
        return "Файл не знайдено!"
    try:
        doc = OpenDocumentText(filename=filename)
        changed = False
        for p in doc.getElementsByType(P):
            if old_text in str(p):
                p.firstChild.data = p.firstChild.data.replace(old_text, new_text, 1)
                changed = True
                break
        if changed:
            doc.save(filename)
            return "Текст замінено."
        else:
            return "Текст для заміни не знайдено."
    except Exception as e:
        return f"Помилка під час заміни тексту: {e}"