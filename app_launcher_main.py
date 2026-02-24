#!/usr/bin/env python3
import sys

from main import run_with_app
from src.apps.core_app import create_app


def main() -> int:
    return run_with_app(create_app, "James's Project Launcher")


if __name__ == "__main__":
    sys.exit(main())
