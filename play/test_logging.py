#!/usr/bin/env python3
"""Small script to exercise the project's `Logger` class.

Runs a few log calls to show formatting, level filtering, and caller detection.
"""
import os
import sys

# Ensure project root is on sys.path so `internal` package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from internal.logging import get_logger, Logger


def module_func():
    log = get_logger()
    log.info("module_func", "From module function")


class Gate:
    def __init__(self):
        self.log = get_logger()

    def open(self):
        self.log.info("Gate", "Gate.open called")

    def debug_action(self):
        self.log.debug("Gate", "Gate debug: {} {}", "x", 123)


def main() -> None:
    print("== default logger ==")
    logger = get_logger()
    logger.info("main", "Info message")
    logger.info("main", "Info message {}", "foo")
    logger.debug("main", "Debug (should be hidden by default)")

    print("\n== set level to DEBUG ==")
    logger.set_level(Logger.DEBUG)
    logger.debug("main", "Now debug appears: {} {}", "A", "B")
    logger.error("main", "An error occurred: {err}", err="boom")

    print("\n== named logger ==")
    named = get_logger(level=Logger.DEBUG)
    named.debug("named", "Named debug: {}", "yay")

    print("\n== caller detection ==")
    module_func()
    g = Gate()
    g.open()
    g.debug_action()


if __name__ == "__main__":
    main()
