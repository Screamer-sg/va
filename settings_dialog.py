import tkinter as tk
from tkinter import ttk

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, voice_settings, assistant_name, wake_word, voice_activation, on_save):
        super().__init__(parent)
        self.title("Налаштування асистента")
        self.resizable(False, False)
        self.voice_settings = voice_settings
        self.on_save = on_save

        # --- Голосові налаштування ---
        tk.Label(self, text="Голос:").grid(row=0, column=0, sticky="e")
        self.voice_var = tk.StringVar(value=self.voice_settings.rhvoice_voice)
        self.voice_combo = ttk.Combobox(self, width=36, textvariable=self.voice_var, state="readonly")
        self.voice_list = self.voice_settings.get_voice_list()
        self.voice_combo['values'] = [f"{code}: {name}" for code, name in self.voice_list]
        self.voice_combo.current(self._find_voice_index(self.voice_settings.rhvoice_voice))
        self.voice_combo.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(self, text="Швидкість:").grid(row=1, column=0, sticky="e")
        self.rate_var = tk.DoubleVar(value=float(self.voice_settings.rhvoice_rate))
        self.rate_scale = tk.Scale(self, from_=-1, to=1, resolution=0.05, orient="horizontal", variable=self.rate_var)
        self.rate_scale.grid(row=1, column=1, sticky="we", padx=5, pady=2)

        # --- Нові поля ---
        tk.Label(self, text="Ім'я асистента:").grid(row=2, column=0, sticky="e")
        self.assistant_name_var = tk.StringVar(value=assistant_name)
        tk.Entry(self, textvariable=self.assistant_name_var, width=36).grid(row=2, column=1, padx=5, pady=2)

        tk.Label(self, text="Фраза активації:").grid(row=3, column=0, sticky="e")
        self.wake_word_var = tk.StringVar(value=wake_word)
        tk.Entry(self, textvariable=self.wake_word_var, width=36).grid(row=3, column=1, padx=5, pady=2)

        self.voice_activation_var = tk.BooleanVar(value=voice_activation)
        tk.Checkbutton(self, text="Голосова активація", variable=self.voice_activation_var).grid(
            row=4, column=0, columnspan=2, pady=4
        )

        frame = tk.Frame(self)
        frame.grid(row=5, column=0, columnspan=2, pady=8)
        tk.Button(frame, text="Перевірити", command=self.test_voice).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="OK", command=self.save_and_close).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Відміна", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _find_voice_index(self, voice_code):
        for idx, (code, _) in enumerate(self.voice_list):
            if code == voice_code:
                return idx
        return 0

    def test_voice(self):
        idx = self.voice_combo.current()
        self.voice_settings.rhvoice_voice = self.voice_list[idx][0]
        self.voice_settings.rhvoice_rate = str(self.rate_var.get())
        self.voice_settings.save()
        # Тут можна вставити speak_text для тесту

    def save_and_close(self):
        idx = self.voice_combo.current()
        self.voice_settings.rhvoice_voice = self.voice_list[idx][0]
        self.voice_settings.rhvoice_rate = str(self.rate_var.get())
        self.voice_settings.save()
        if self.on_save:
            self.on_save(
                self.assistant_name_var.get(),
                self.wake_word_var.get(),
                self.voice_activation_var.get()
            )
        self.destroy()