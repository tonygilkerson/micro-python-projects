"""Minimal console logger compatible with MicroPython (RPi Pico).

This logger removes stack inspection and complex datetime usage so it
can run on constrained MicroPython builds. It prints a simple timestamp,
level, and message. Keep the API small: `Logger` with `debug`, `info`,
`error`, and `set_level`.
"""

import time


class Logger:
	DEBUG = 10
	INFO = 20
	ERROR = 30

	_LEVEL_NAMES = {DEBUG: "DEBUG", INFO: "INFO", ERROR: "ERROR"}

	def __init__(self, level: int = INFO):
		self.level = level

	def set_level(self, level: int) -> None:
		self.level = level

	def debug(self, source, msg, *args, **kwargs) -> None:
		self._log(self.DEBUG, source, msg, *args, **kwargs)

	def info(self, source, msg, *args, **kwargs) -> None:
		self._log(self.INFO, source, msg, *args, **kwargs)

	def error(self, source, msg, *args, **kwargs) -> None:
		self._log(self.ERROR, source, msg, *args, **kwargs)

	def _log(self, level: int, source, msg, *args, **kwargs) -> None:
		if level < self.level:
			return

		try:
			message = msg.format(*args, **kwargs) if (args or kwargs) and isinstance(msg, str) else str(msg)
		except Exception:
			message = str(msg)

		# Build a simple timestamp. Use time.localtime when available and
		# get milliseconds from ticks_ms if present. Fall back to time.time.
		try:
			t = time.localtime()
			if hasattr(time, "ticks_ms"):
				ms = time.ticks_ms() % 1000
			else:
				ms = int((time.time() * 1000) % 1000)
			ts = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{:03d}".format(
				t[0], t[1], t[2], t[3], t[4], t[5], ms
			)
		except Exception:
			# Very minimal fallback
			try:
				ts = "t={}".format(int(time.time()))
			except Exception:
				ts = ""

		level_name = self._LEVEL_NAMES.get(level, str(level))
		src = str(source)
		print("[{}] {} {} - {}".format(ts, level_name, src, message))


def get_logger(level: int = Logger.INFO) -> Logger:
	return Logger(level=level)


__all__ = ["Logger", "get_logger"]

