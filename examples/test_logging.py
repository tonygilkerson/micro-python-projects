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
        # pre-format using f-string
        self.log.debug("Gate", f"Gate debug: {'x'} {123}")


def main() -> None:
    print("== default logger ==")
    logger = get_logger()
    logger.info("main", "Info message")
    # pre-format using f-string
    logger.info("main", f"Info message {'foo'}")
    logger.debug("main", "Debug (should be hidden by default)")

    print("\n== set level to DEBUG ==")
    logger.set_level(Logger.DEBUG)
    # pre-format using f-string
    logger.debug("main", f"Now debug appears: {'A'} {'B'}")
    # pre-format kwargs into the message using f-string
    logger.error("main", f"An error occurred: {'boom'}")

    print("\n== named logger ==")
    named = get_logger(level=Logger.DEBUG)
    named.debug("named", f"Named debug: {'yay'}")

    print("\n== caller detection ==")
    module_func()
    g = Gate()
    g.open()
    g.debug_action()


if __name__ == "__main__":
    main()
