import json
import os

SETTINGS_FILE = "user_settings.json"

class VoiceSettings:
    def __init__(self):
        self.rhvoice_voice = "natalia"
        self.rhvoice_lang = "uk-UA"
        self.rhvoice_rate = "0"  # RHVoice: -1 (повільно), 0 (норм), 1 (швидко)
        self._load()

    def to_dict(self):
        return {
            "rhvoice_voice": self.rhvoice_voice,
            "rhvoice_lang": self.rhvoice_lang,
            "rhvoice_rate": self.rhvoice_rate
        }

    def from_dict(self, d):
        self.rhvoice_voice = d.get("rhvoice_voice", self.rhvoice_voice)
        self.rhvoice_lang = d.get("rhvoice_lang", self.rhvoice_lang)
        self.rhvoice_rate = d.get("rhvoice_rate", self.rhvoice_rate)

    def save(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.from_dict(data)
            except Exception:
                pass

    def get_voice_list(self):
        # Тільки ті голоси, що є у вашій системі
        return [
            ("anatol", "Анатолій (чоловічий)"),
            ("marianna", "Маріанна (жіночий)"),
            ("natalia", "Наталя (жіночий)"),
            ("volodymyr", "Володимир (чоловічий)")
        ]

    def get_voice_name(self, voice_id):
        names = dict(self.get_voice_list())
        return names.get(voice_id, voice_id)

voice_settings = VoiceSettings()
