import time
import threading


class WatchDog(object):

    def __init__(self, timeout_func, timeout_in_seconds=10):
        self.last_activity = time.time()
        self.timeout_in_seconds = timeout_in_seconds
        self.timeout_func = timeout_func

    def run(self):
        watchdog_thread = threading.Thread(target=self._watchdog)
        self.process_still_active()
        watchdog_thread.start()

    def _watchdog(self):
        while time.time() - self.last_activity < self.timeout_in_seconds:
            time.sleep(1)
        self.timeout_func()

    def process_still_active(self):
        self.last_activity = time.time()
