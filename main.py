import threading
from speech_tools import speak_text
from voice_listener import listen_for_user_speech

def main():
    while True:
        print("\nСкажіть команду (або 'вийти' для завершення):")
        user_text = speech_tools.recognize_speech_from_mic()
        if "вийти" in user_text.lower():
            break
        print(f"Ви сказали: {user_text}")
        response = generate_response(user_text)
        print(f"Асистент: {response}")
        speech_tools.speak_text(response)
def speak_with_interrupt(text):
    listener_thread = threading.Thread(target=listen_for_user_speech)
    listener_thread.start()
    speak_text(text)
    listener_thread.join()

if __name__ == "__main__":
    main()
