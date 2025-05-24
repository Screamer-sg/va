import os
import fnmatch

def find_files(directory, pattern, ext=None):
    """
    Пошук файлів у вказаній теці (рекурсивно) за шаблоном у назві та/або розширенням.
    directory: де шукати
    pattern: частина назви файлу (без розширення)
    ext: наприклад ".odt" або ".xlsx" (може бути None)
    """
    matches = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if pattern.lower() in filename.lower():
                if ext is None or filename.lower().endswith(ext.lower()):
                    matches.append(os.path.join(root, filename))
    return matches