"""Minimal console logger compatible with MicroPython (RPi Pico)."""

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

	def debug(self, source, msg) -> None:
		self._log(self.DEBUG, source, msg)

	def info(self, source, msg) -> None:
		self._log(self.INFO, source, msg)

	def error(self, source, msg) -> None:
		self._log(self.ERROR, source, msg)

	def _log(self, level: int, source, msg) -> None:
		if level < self.level:
			return

		try:
			message = str(msg)
		except Exception:
			message = ""

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

# DEVTODO I dont think i need a function to create the class instance
def get_logger(level: int = Logger.INFO) -> Logger:
	return Logger(level=level)


__all__ = ["Logger", "get_logger"]

