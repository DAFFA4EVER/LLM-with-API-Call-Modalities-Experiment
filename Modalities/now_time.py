def now_time():
    from datetime import datetime

    # Getting the current date and time
    current_time = datetime.now()

    return current_time.strftime("%Y-%m-%d %H:%M:%S")
