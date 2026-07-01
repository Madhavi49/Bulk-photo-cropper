#!/usr/bin/env python
"""Compatibility launcher for the Django version of the app.

The original project started from this file as a Flask app. The application
logic now lives in config/cropper/views.py, and this file simply forwards to
Django so `python app.py` still starts the project.
"""
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
DJANGO_DIR = ROOT_DIR / "config"


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    sys.path.insert(0, str(DJANGO_DIR))

    from django.core.management import execute_from_command_line

    command = sys.argv if len(sys.argv) > 1 else [sys.argv[0], "runserver"]
    execute_from_command_line(command)


if __name__ == "__main__":
    main()
