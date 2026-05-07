"""Centralized env var documentation. Handlers/services read os.getenv directly,
this module is the canonical list of what needs to be configured."""
import os
from dotenv import load_dotenv

load_dotenv()

# Required
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Optional — WordPress publishing
WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD")
WP_DEFAULT_STATUS = os.getenv("WP_DEFAULT_STATUS", "draft")  # draft | publish

# Optional — Telegram channel publishing
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")  # numeric -100... or @username

# Optional — Claude model override
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
