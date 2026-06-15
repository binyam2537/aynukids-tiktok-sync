"""
Configuration management for AynuKids backend.
All sensitive values are loaded from environment variables.
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    # Also check backend/.env for convenience
    _env_path_local = Path(__file__).resolve().parent / ".env"
    if _env_path_local.exists():
        load_dotenv(_env_path_local)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("aynukids")

# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# ---------------------------------------------------------------------------
# TikTok channel
# ---------------------------------------------------------------------------
TIKTOK_HANDLE: str = os.getenv("TIKTOK_HANDLE", "aynukids")
TIKTOK_PROFILE_URL: str = f"https://www.tiktok.com/@{TIKTOK_HANDLE}"

# ---------------------------------------------------------------------------
# Scraping behaviour
# ---------------------------------------------------------------------------
# Minimum and maximum delay (seconds) between oEmbed requests
REQUEST_DELAY_MIN: float = float(os.getenv("REQUEST_DELAY_MIN", "2.0"))
REQUEST_DELAY_MAX: float = float(os.getenv("REQUEST_DELAY_MAX", "5.0"))

# Maximum number of videos to process in a single run (0 = unlimited)
MAX_VIDEOS_PER_RUN: int = int(os.getenv("MAX_VIDEOS_PER_RUN", "0"))

# Active provider for channel scraping: "ytdlp" or future providers like "apify"
CHANNEL_PROVIDER: str = os.getenv("CHANNEL_PROVIDER", "ytdlp")

# Active provider for sound scraping: "ytdlp" or future providers like "apify"
SOUND_PROVIDER: str = os.getenv("SOUND_PROVIDER", "ytdlp")


def validate_config() -> None:
    """Validate that all required configuration values are present."""
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")

    if missing:
        logger.error(
            "Missing required environment variables: %s. "
            "Please set them in your .env file or environment.",
            ", ".join(missing),
        )
        sys.exit(1)

    logger.info("Configuration validated successfully.")
    logger.info("  Supabase URL: %s", SUPABASE_URL[:30] + "...")
    logger.info("  TikTok Handle: @%s", TIKTOK_HANDLE)
    logger.info("  Channel Provider: %s", CHANNEL_PROVIDER)
    logger.info("  Sound Provider: %s", SOUND_PROVIDER)
