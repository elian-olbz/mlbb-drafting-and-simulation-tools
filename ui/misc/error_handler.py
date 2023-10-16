import sys
import traceback
from datetime import datetime

def log_error(error_message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("errors.log", 'a') as log_file:
        log_file.write(f"{current_time} - {error_message}")
        log_file.write('-' * 75 + '\n')  # Add a separator line

def excepthook(type, value, traceback_obj):
    formatted_traceback = "".join(traceback.format_tb(traceback_obj))
    error_message = f"{type.__name__}: {value}\n{formatted_traceback}"
    log_error(error_message)
    print(error_message)
