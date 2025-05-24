import platform
import subprocess

def set_volume(level):
    """Встановити рівень гучності (0-100)"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["amixer", "sset", "Master", f"{level}%"])
        else:
            return "Операційна система не підтримується."
        return f"Гучність встановлено на {level}%"
    except Exception as e:
        return f"Не вдалося змінити гучність: {e}"

def change_volume(delta):
    """Збільшити/зменшити гучність на delta"""
    try:
        if platform.system() == "Linux":
            sign = "+" if delta > 0 else "-"
            subprocess.run(["amixer", "sset", "Master", f"{abs(delta)}%{sign}"])
        else:
            return "Операційна система не підтримується."
        return f"Гучність змінено."
    except Exception as e:
        return f"Не вдалося змінити гучність: {e}"

def mute_volume():
    try:
        if platform.system() == "Linux":
            subprocess.run(["amixer", "sset", "Master", "mute"])
        else:
            return "Операційна система не підтримується."
        return "Звук вимкнено."
    except Exception as e:
        return f"Не вдалося вимкнути звук: {e}"

def unmute_volume():
    try:
        if platform.system() == "Linux":
            subprocess.run(["amixer", "sset", "Master", "unmute"])
        else:
            return "Операційна система не підтримується."
        return "Звук увімкнено."
    except Exception as e:
        return f"Не вдалося увімкнути звук: {e}"

def toggle_wifi(enable):
    """Увімкнути/вимкнути Wi-Fi"""
    try:
        if platform.system() == "Linux":
            state = "on" if enable else "off"
            subprocess.run(["nmcli", "radio", "wifi", state])
        else:
            return "Операційна система не підтримується."
        return f"Wi-Fi {'увімкнено' if enable else 'вимкнено'}."
    except Exception as e:
        return f"Не вдалося змінити стан Wi-Fi: {e}"

def toggle_bluetooth(enable):
    """Увімкнути/вимкнути Bluetooth"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["rfkill", "unblock" if enable else "block", "bluetooth"])
        else:
            return "Операційна система не підтримується."
        return f"Bluetooth {'увімкнено' if enable else 'вимкнено'}."
    except Exception as e:
        return f"Не вдалося змінити стан Bluetooth: {e}"

def system_sleep():
    """Відправити систему у сплячий режим"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["systemctl", "suspend"])
        else:
            return "Операційна система не підтримується."
        return "Система перейшла у сплячий режим."
    except Exception as e:
        return f"Не вдалося відправити у сплячий режим: {e}"

def system_hibernate():
    """Відправити систему у гібернацію"""
    try:
        if platform.system() == "Linux":
            subprocess.run(["systemctl", "hibernate"])
        else:
            return "Операційна система не підтримується."
        return "Система гібернована."
    except Exception as e:
        return f"Не вдалося гібернувати систему: {e}"