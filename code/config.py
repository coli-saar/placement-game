"""Example config file. Contains global variables meant to be used read-only."""

import os
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
OPENAI_API_KEY = 'YOUR-OPENAI-API-KEY'

TIMEOUT_TIMER = 10  # round max time

# colored messages
COLOR_MESSAGE = '<a style="color:{color};">{message}</a>'
WELCOME = '<h3 style="color:{color};">{message}</h3>'
STANDARD_COLOR = "Purple"
WARNING_COLOR = "FireBrick"
SUCCESS_COLOR = "Green"
TASK_TITLE = "Object placement game"