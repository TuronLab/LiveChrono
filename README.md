# LiveChrono
[![PyPI version](https://img.shields.io/pypi/v/live-chrono.svg)](https://pypi.org/project/live-chrono/)

<p align="center">
    <img src="https://raw.githubusercontent.com/turonlab/LiveChrono/master/assets/logo-default.png" alt="LiveChrono logo" width="300" style="border-radius: 5px;">
</p>

LiveChrono is a lightweight, dependency-free Python package that shows a live updating stopwatch in the terminal, with pause/resume support and millisecond precision.

<p align="center">
    <img src="https://raw.githubusercontent.com/turonlab/LiveChrono/master/assets/demo.gif" alt="Demo of LiveChrono in action" width="350">
</p>

---

## Why LiveChrono?

Perfect for CLI scripts, quick profiling, demo timers, and any situation where a human-friendly live elapsed display is handy.

- **Tiny & dependency-free** — single module, minimal surface area.
- **Human-friendly customizable output** — `HH:MM:SS.ms` by default; fully customizable with format tokens.
- **Interruptible & accurate** — pause/resume support; uses `time.perf_counter()` for elapsed measurement.

---


## Installation

Install from PyPI:

```bash
pip install live-chrono
```

---

## Features

- **Real-time terminal display on a single line** that updates at a configurable interval.
- **Customizable format tokens** (see below).
- **Pause/resume** the chrono to measure the execution time of the desired methods.
- **Context-manager friendly** (`with LiveChrono()`).
- Returns a `ChronoResult` object with wall-clock timestamps and elapsed seconds.

---

## Format Tokens

| Token | Meaning                |
| ----- |------------------------|
| `%D`  | days (unlimited)       |
| `%H`  | hours (00-23)          |
| `%M`  | minutes (00–59)        |
| `%S`  | seconds (00–59)        |
| `%f`  | milliseconds (000–999) |
| `%ms` | alias for milliseconds |

> **Note**: Lower units roll over only if you include the higher unit.  
> Example: a format string with only `%S` may display `120` for two minutes.

---

## Quickstart

Basic usage (context manager — recommended):

```python
from live_chrono import LiveChrono
import time

with LiveChrono():
    time.sleep(0.35)
```

Pause/resume and capture the result with a custom output format:

```python
from live_chrono import LiveChrono
import time

with LiveChrono(display_format="Elapsed: %S seconds and %f ms") as chrono:
    time.sleep(2.30)  # simulate work
    chrono.pause()    # temporary chrono pause  
    time.sleep(1)     # simulate non-relevant work for timer
    chrono.resume()   # resume the chrono  
    time.sleep(2.2)

# timer.result is available after the context exits
res = chrono.result
print(f"Elapsed seconds: {res.elapsed:.3f}")
# prints something like: Elapsed: 04 seconds and 500 ms
```

Manual start / pause / resume /stop:

```python
from live_chrono import LiveChrono
import time

chrono = LiveChrono(update_interval=0.05)
chrono.start()
time.sleep(0.2)  # simulate work

chrono.pause()  # stop counting, display indicates paused
time.sleep(0.2)  # this work does NOT count for the chrono

chrono.resume()  # continue measuring the elapsed time
time.sleep(0.15)

result = chrono.stop()  # stops background thread, returns ChronoResult
print("Final:", result.elapsed)  # float seconds (e.g. 0.35)
```

---

## API Reference

### LiveChrono

`LiveChrono(update_interval=0.1, display_format="Elapsed: %H:%M:%S.%f")`

Create a live-updating timer.

**Parameters**  
- **update_interval** (*float*, default `0.1`) – Refresh rate in seconds. Lower values update the display more frequently.  
- **display_format** (*str*, default `"Elapsed: %H:%M:%S.%f"`) – Format string for rendering elapsed time (see format tokens above).

### Methods

- `start() → LiveChrono` – Begin timing and return the instance.  
- `stop() → ChronoResult` – Stop timing, join the background thread, and return a `ChronoResult`.  
- `pause()` – Pause the timer. No effect if already paused. Raises `RuntimeError` if called before `start()`.  
- `resume()` – Resume from a paused state. No effect if not paused.  
- `__enter__() / __exit__()` – Context-manager support.  

`ChronoResult` object

The `ChronoResult` model contains:

- `start_time`: wall-clock start time (UNIX epoch seconds)
- `end_time`: wall-clock end time (UNIX epoch seconds)
- `elapsed`: elapsed time in seconds (float)
- `elapsed_format`: elapsed time formated according the `display_format`
- `display_format`: the format string used

## Notes & Best Practices

- The timer uses `time.perf_counter()` for high-resolution measurement of elapsed intervals, while `time.time()` is 
  used for wall-clock `start_time` and `end_time`.
- Small variations (a few ms) may appear due to thread scheduling or terminal printing.
- Output is printed to `stdout` on a single line that refreshes each update.
- The `update_interval` affects display smoothness only, not timing accuracy. 
- Multiple pause/resume cycles are supported, with elapsed time accumulating only while the timer is running.
- For CLI usage, avoid extremely low `update_interval` values on slow terminals — printing overhead may affect readability.

## License

This project is licensed under the MIT License.

You are free to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the software, provided that the copyright notice
and permission notice appear in all copies.

See the [LICENSE](https://github.com/TuronLab/LiveChrono/blob/master/LICENSE)
 file for the full text.
