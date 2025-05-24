import os
from utils import get_current_timestamp

def log_event(event, log_file="./logs/assistant.log"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{get_current_timestamp()} | {event}\n")