import threading
import time
from datetime import datetime, timedelta, timezone

from .runtime import monitor


IST = timezone(timedelta(hours=5, minutes=30), name='IST')


class DailyISTScheduler(object):
    def __init__(self, callback, hour=16, minute=30):
        self.callback = callback
        self.hour = int(hour)
        self.minute = int(minute)
        self._stop = threading.Event()
        self._thread = None

    def next_run_time(self, now=None):
        now = now or datetime.now(IST)
        target = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    def _loop(self):
        while not self._stop.is_set():
            target = self.next_run_time()
            monitor.scheduler(True, target, 'Asia/Kolkata')
            while not self._stop.is_set():
                remaining = (target - datetime.now(IST)).total_seconds()
                if remaining <= 0:
                    break
                self._stop.wait(min(max(remaining, 1.0), 30.0))
            if self._stop.is_set():
                break
            try:
                self.callback()
            except Exception as exc:
                monitor.event('error', 'Scheduled run failed: {0}'.format(exc))
            # Avoid a second trigger within the same minute.
            self._stop.wait(61.0)
        monitor.scheduler(False, None, 'Asia/Kolkata')

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name='daily-ist-scheduler')
        self._thread.daemon = True
        self._thread.start()
        monitor.event('success', 'Scheduler active for {0:02d}:{1:02d} Asia/Kolkata.'.format(self.hour, self.minute))

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
