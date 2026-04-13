import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your-token-here":
    raise ValueError(
        "Set TELEGRAM_BOT_TOKEN in .env file. Get one from @BotFather on Telegram."
    )

# HuggingFace Space running Chandra OCR 2 on ZeroGPU
HF_SPACE_ID = "victor/chandra-ocr-2"

# Directory for temporary image files
TMP_DIR = os.path.join(os.path.dirname(__file__), "tmp")
os.makedirs(TMP_DIR, exist_ok=True)
