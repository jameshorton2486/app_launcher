#!/usr/bin/env python3
import sys

from main import run_with_app
from src.apps.tools_app import create_app


def main() -> int:
    return run_with_app(create_app, "App Launcher Power Tools")


if __name__ == "__main__":
    sys.exit(main())
