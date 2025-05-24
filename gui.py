import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import speech_tools
from assistant_core import generate_response
from settings import voice_settings
import math
import time
from voice_listener import listen_for_user_speech
from speech_tools import speak_text

class CircularEqualizer(tk.Canvas):
    def __init__(self, parent, bars=16, radius=40, **kwargs):
        super().__init__(parent, width=2*radius+20, height=2*radius+20, bg="white", highlightthickness=0, **kwargs)
        self.bars = bars
        self.radius = radius
        self.angles = [i * 2 * math.pi / self.bars for i in range(self.bars)]
        self.amplitudes = [0] * self.bars
        self.items = []
        self.center = (radius+10, radius+10)
        self.max_bar_len = radius * 0.7
        self._init_bars()
        self.running = False

    def _init_bars(self):
        self.items = []
        for i in range(self.bars):
            angle = self.angles[i]
            x0 = self.center[0] + self.radius * math.cos(angle)
            y0 = self.center[1] + self.radius * math.sin(angle)
            x1 = self.center[0] + (self.radius + self.max_bar_len) * math.cos(angle)
            y1 = self.center[1] + (self.radius + self.max_bar_len) * math.sin(angle)
            item = self.create_line(x0, y0, x1, y1, width=5, fill="#38f")
            self.items.append(item)

    def animate(self, amplitudes_seq, speed=0.03):
        self.running = True
        for amps in amplitudes_seq:
            if not self.running:
                break
            self.draw_frame(amps)
            self.update()
            time.sleep(speed)
        self.running = False

    def stop(self):
        self.running = False

    def draw_frame(self, amps):
        for i, amplitude in enumerate(amps):
            angle = self.angles[i]
            bar_len = self.max_bar_len * amplitude
            x0 = self.center[0] + self.radius * math.cos(angle)
            y0 = self.center[1] + self.radius * math.sin(angle)
            x1 = self.center[0] + (self.radius + bar_len) * math.cos(angle)
            y1 = self.center[1] + (self.radius + bar_len) * math.sin(angle)
            self.coords(self.items[i], x0, y0, x1, y1)

    def reset(self):
        self.draw_frame([0]*self.bars)
        self.update()

def generate_fake_eq_sequence(duration_sec=2.5, bars=16, fps=30):
    import random
    frames = int(duration_sec * fps)
    seq = []
    for t in range(frames):
        amps = [0.2 + 0.7*abs(math.sin(2*math.pi*(i/float(bars) + t*0.03 + random.uniform(-0.1,0.1))))
                for i in range(bars)]
        amps = [min(1.0, max(0.05, amp + random.uniform(-0.08, 0.08))) for amp in amps]
        seq.append(amps)
    return seq

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, voice_settings, assistant_name, wake_word, voice_activation, on_save):
        super().__init__(parent)
        self.title("Налаштування асистента")
        self.resizable(False, False)
        self.voice_settings = voice_settings
        self.on_save = on_save

        # Голосові налаштування
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

        # Нові поля
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
        speak_text("Це тестове повідомлення. Голосові налаштування застосовано.")

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

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Голосовий асистент")
        self.last_response = "" 
        # --- Змінні для налаштувань ---
        self.assistant_name = "Асистент"
        self.wake_word = "асистент"
        self.voice_activation = True
        self.create_widgets()

    def speak_with_interrupt(self, text):
        listener_thread = threading.Thread(target=listen_for_user_speech)
        listener_thread.start()
        speak_text(text)
        listener_thread.join()    

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Налаштування", menu=settings_menu)
        settings_menu.add_command(label="Налаштування асистента...", command=self.open_settings)

        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.BOTH, expand=False)
        self.eq = CircularEqualizer(top_frame, bars=16, radius=40)
        self.eq.pack(side=tk.LEFT, padx=10, pady=10)
        self.textbox = scrolledtext.ScrolledText(top_frame, width=60, height=15)
        self.textbox.pack(side=tk.LEFT, padx=10, pady=10)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=(0,10))
        self.entry = tk.Entry(bottom_frame, width=50)
        self.entry.pack(side=tk.LEFT, padx=(10, 0))

        self.send_btn = tk.Button(bottom_frame, text="Надіслати", command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=5)
        self.voice_btn = tk.Button(bottom_frame, text="🎤 Говорити", command=self.on_voice)
        self.voice_btn.pack(side=tk.LEFT, padx=5)

    def open_settings(self):
        SettingsDialog(
            self.root,
            voice_settings,
            self.assistant_name,
            self.wake_word,
            self.voice_activation,
            self.save_settings_callback
        )

    def save_settings_callback(self, assistant_name, wake_word, voice_activation):
        self.assistant_name = assistant_name
        self.wake_word = wake_word
        self.voice_activation = voice_activation

    def on_send(self):
        user_text = self.entry.get()
        if not user_text.strip():
            return
        self.textbox.insert(tk.END, f"Ви: {user_text}\n")
        self.entry.delete(0, tk.END)
        threading.Thread(target=self.process, args=(user_text,)).start()

    def on_voice(self):
        if self.voice_activation:
            self.textbox.insert(tk.END, f"Скажіть фразу активації: '{self.wake_word}'...\n")
            activated = speech_tools.listen_for_wake_word([self.wake_word])
            if not activated:
                self.textbox.insert(tk.END, "Активаційна фраза не розпізнана.\n")
                return
        self.textbox.insert(tk.END, "Говоріть...\n")
        threading.Thread(target=self._voice_capture).start()

    def _voice_capture(self):
        user_text = speech_tools.recognize_speech_from_mic()
        self.textbox.insert(tk.END, f"Ви (голос): {user_text}\n")
        self.process(user_text)

    def process(self, user_text):
        # Передаємо останню відповідь у generate_response
        response = generate_response(user_text, last_response=self.last_response)
        self.textbox.insert(tk.END, f"{self.assistant_name}: {response}\n")
        self.last_response = response  # Оновлюємо після нової відповіді
        eq_thread = threading.Thread(target=self.animate_equalizer_while_speaking, args=(response,))
        eq_thread.start()
        self.speak_with_interrupt(response)
        self.eq.stop()
        self.eq.reset()

    def animate_equalizer_while_speaking(self, response_text):
        duration = max(1.5, min(6.0, len(response_text) * 0.06))
        seq = generate_fake_eq_sequence(duration_sec=duration, bars=self.eq.bars)
        self.eq.animate(seq, speed=0.03)

def run_gui():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
