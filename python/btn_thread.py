import threading
import tkinter as tk
import time

duration = 1  # Duration in seconds
bg_thread = None

class BackgroundThread(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def run(self):
        start_time = time.time()  # Record the start time
        
        end_time = threading.Event()
        timer = threading.Timer(duration, end_time.set)
        timer.start()
        
        while not end_time.is_set():
            method_to_trigger()
        
        elapsed_time_ms = (time.time() - start_time) * 1000  # Calculate elapsed time in milliseconds
        print(f"Thread ran for: {elapsed_time_ms:.2f} milliseconds")

    def stop(self):
        self._stop_event.set()

def start_trigger(new_duration):
    global bg_thread, duration
    duration =new_duration
    print("Staring triggerr!!")
    if not bg_thread or not bg_thread.is_alive():
        bg_thread = BackgroundThread()
        bg_thread.start()

def stop_trigger():
    global bg_thread
    if bg_thread and bg_thread.is_alive():
        bg_thread.stop()
        bg_thread.join()
        bg_thread = None

def method_to_trigger():
    # Replace this with the method you want to trigger
    pass



