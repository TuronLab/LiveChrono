import time
import threading
from typing import Optional

from .model import ChronoResult
from .utils import validate_time_format


class LiveChrono:
    """
    Live-updating elapsed-time display with configurable output format.
    Includes pause/resume controls.

    Format tokens supported in format_str:
      %H   - hours (zero-padded, can exceed 23)
      %M   - minutes (00-59)
      %S   - seconds (00-59)
      %f   - milliseconds (000-999)   <-- new
      %ms  - alternative token for milliseconds
    Default format: "Elapsed: %H:%M:%S.%f"
    """

    def __init__(self, update_interval: float = 0.1, format_str: str = "Elapsed: %H:%M:%S.%f"):
        validate_time_format(format_str)
        self.update_interval = update_interval
        self.format_str = format_str

        self._start_perf: Optional[float] = None
        self._start_wall: Optional[float] = None
        self._paused_elapsed: float = 0.0
        self._paused: bool = False

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # not paused initially

        self.result: Optional[ChronoResult] = None
        self._lock = threading.Lock()

    def _current_elapsed(self) -> float:
        """
        Compute the current elapsed time without modifying state.
        Safe to call from the worker thread.
        """
        if self._start_perf is None:
            return self._paused_elapsed
        if self._paused:
            return self._paused_elapsed
        return self._paused_elapsed + (time.perf_counter() - self._start_perf)

    def _format_elapsed(self, elapsed: float) -> str:
        # Start from largest to smallest
        total_seconds = int(elapsed)
        milliseconds = int(round((elapsed - total_seconds) * 1000))

        s = self.format_str

        # Decide which units are present
        show_days = "%D" in s
        show_hours = "%H" in s
        show_minutes = "%M" in s
        show_seconds = "%S" in s or "%TS" in s

        days = total_seconds // 86400 if show_days else 0
        hours = (total_seconds // 3600) % 24 if show_hours else total_seconds // 3600
        minutes = (total_seconds // 60) % 60 if show_minutes else total_seconds // 60
        seconds = total_seconds % 60 if show_seconds and show_minutes else total_seconds

        # Replace tokens
        if show_days:
            s = s.replace("%D", f"{days}")
        if show_hours:
            s = s.replace("%H", f"{hours:02d}")
        if show_minutes:
            s = s.replace("%M", f"{minutes:02d}")
        if "%S" in s:
            s = s.replace("%S", f"{seconds:02d}")
        if "%f" in s:
            s = s.replace("%f", f"{milliseconds:03d}")
        if "%ms" in s:
            s = s.replace("%ms", f"{milliseconds:03d}")

        return s

    def _run(self):
        # Regularly print the formatted elapsed time while running.
        try:
            while not self._stop_event.is_set():
                # wait will block if paused; it returns immediately if set
                self._pause_event.wait()

                # It's possible stop was set while waiting, re-check
                if self._stop_event.is_set():
                    break

                elapsed = self._current_elapsed()
                msg = self._format_elapsed(elapsed)
                # print on a single line
                print(f"\r{msg}", end="", flush=True)

                # Sleep in small increments to be responsive to stop/pause
                time.sleep(self.update_interval)

            # When stop requested, compute final result
            with self._lock:
                if self.result is None:
                    total = self._paused_elapsed if self._paused else self._current_elapsed()
                    self.result = ChronoResult(
                        start_time=self._start_wall,
                        end_time=time.time(),
                        elapsed=total,
                        format_str=self.format_str,
                    )
            # Print final line (move to newline)
            print(f"\r{self._format_elapsed(self.result.elapsed)}")
        except Exception:
            # Ensure exceptions don't silently kill thread without producing a result
            with self._lock:
                if self.result is None:
                    self.result = ChronoResult(
                        start_time=self._start_wall,
                        end_time=time.time(),
                        elapsed=self._paused_elapsed,
                        format_str=self.format_str,
                    )
            raise

    def start(self):
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Timer is already running.")
        # reset state
        self._start_perf = time.perf_counter()
        self._start_wall = time.time()
        self._paused_elapsed = 0.0
        self._paused = False
        self._stop_event.clear()
        self._pause_event.set()
        self.result = None

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def stop(self) -> ChronoResult:
        # Must have been started at least once
        if not self._thread:
            raise RuntimeError("Timer was never started.")
        # Signal the thread to stop and ensure it's not blocked on pause
        self._stop_event.set()
        self._pause_event.set()
        self._thread.join()
        assert self.result is not None
        return self.result

    def pause(self):
        if self._paused:
            return
        if not self._thread:
            raise RuntimeError("Timer was never started.")
        # Capture elapsed up to now and mark paused
        now = time.perf_counter()
        if self._start_perf is not None:
            self._paused_elapsed += now - self._start_perf
        self._paused = True
        # Block the run loop until resumed
        self._pause_event.clear()
        print(" - Paused", end="")
        return self.result

    def resume(self):
        if not self._paused:
            return
        # Start counting from now
        self._start_perf = time.perf_counter()
        self._paused = False
        self._pause_event.set()

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
