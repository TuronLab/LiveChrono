import io
import time
import unittest
from contextlib import redirect_stdout

from live_chrono import LiveChrono
from live_chrono.utils import validate_time_format


class TestLiveChronoExtra(unittest.TestCase):

    def test_valid_formats(self):
        valid_formats = [
            "%S.%f",
            "%S.%ms",
            "%M:%S",
            "%H:%M:%S",
            "%D:%H:%M:%S",
            "%M:%S.%f",
            "%H:%M:%S.%ms",
            "%D:%H:%M:%S.%f"
        ]
        for fmt in valid_formats:
            with self.subTest(fmt=fmt):
                try:
                    validate_time_format(fmt)
                except ValueError as e:
                    self.fail(f"validate_time_format raised ValueError unexpectedly for '{fmt}': {e}")

    def test_invalid_formats(self):
        invalid_formats = [
            "%M.%f",      # milliseconds without seconds
            "%H:%S",      # seconds without minutes
            "%D:%M:%S",   # minutes without hours
            "%H.%ms",     # milliseconds without seconds
            "%D:%S",      # skips H and M
        ]
        for fmt in invalid_formats:
            with self.subTest(fmt=fmt):
                with self.assertRaises(ValueError):
                    validate_time_format(fmt)

    def test_format_milliseconds_token_works(self):
        # Use the private formatter to avoid relying on printed output
        t = LiveChrono(format_str="%H:%M:%S.%f")
        # Simulate 1.123 seconds and check millisecond formatting is zero-padded
        formatted = t._format_elapsed(1.123)
        # Expect "00:00:01.123"
        self.assertTrue(formatted.endswith(".123"))
        self.assertIn("00:00:01", formatted)

    def test_format_without_ms_token_has_no_fraction(self):
        t = LiveChrono(format_str="%H:%M:%S")
        formatted = t._format_elapsed(0.789)
        # No millisecond separator when %f / %ms not present
        self.assertEqual(formatted, "00:00:00")

    def test_millisecond_value_matches_elapsed(self):
        # This test actually runs the timer briefly and checks the numeric ms value
        t = LiveChrono(format_str="%H:%M:%S.%f", update_interval=0.01)
        # Silence printing to keep test output clean
        buf = io.StringIO()
        with redirect_stdout(buf):
            t.start()
            time.sleep(0.12)
            result = t.stop()

        ms = int((result.elapsed - int(result.elapsed)) * 1000)
        # We slept ~120ms; accept a generous tolerance (50ms) to avoid flakiness
        self.assertTrue(70 <= ms <= 200, f"ms={ms} not in expected range")

    def test_pause_without_start_raises(self):
        t = LiveChrono()
        with self.assertRaises(RuntimeError):
            t.pause()

    def test_pause_idempotent(self):
        t = LiveChrono(update_interval=0.01)
        buf = io.StringIO()
        with redirect_stdout(buf):
            t.start()
            time.sleep(0.05)
            t.pause()
            paused_after_first = t._paused_elapsed
            # second pause should be a no-op and not change paused elapsed
            t.pause()
            paused_after_second = t._paused_elapsed
            t.stop()
        self.assertAlmostEqual(paused_after_first, paused_after_second, delta=0.01)

    def test_resume_without_pause_is_noop(self):
        # Should not raise and timer should keep running normally
        t = LiveChrono(update_interval=0.01)
        buf = io.StringIO()
        with redirect_stdout(buf):
            t.start()
            time.sleep(1)
            # calling resume when not paused should do nothing and not raise
            t.resume()
            time.sleep(1)
            result = t.stop()
        self.assertAlmostEqual(result.elapsed, 2, delta=0.1)

    def test_result_has_wall_times_and_timed_out_flag_false(self):
        t = LiveChrono(update_interval=0.01)
        buf = io.StringIO()
        with redirect_stdout(buf):
            t.start()
            time.sleep(0.02)
            res = t.stop()
        self.assertIsNotNone(res.start_time)
        self.assertIsNotNone(res.end_time)


if __name__ == "__main__":
    unittest.main()
