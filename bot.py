"""
Telegram bot that transcribes handwritten text from photos.

Send a photo of handwriting to the bot and it will reply with
the extracted text using Chandra OCR 2.
"""

import asyncio
import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, TMP_DIR
from ocr import extract_text, warmup_client

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "Hi! Send me a photo of handwritten text and I'll transcribe it for you.\n\n"
        "Just take a clear photo and send it here. I'll do my best to read the handwriting!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Take a photo of handwritten text\n"
        "2. Send the photo to this chat\n"
        "3. Wait for the transcription (this can take a few minutes on CPU)\n\n"
        "Tips for best results:\n"
        "- Use good lighting\n"
        "- Keep the paper flat\n"
        "- Try to capture the full page\n"
        "- Avoid shadows on the text"
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos -- download, OCR, and reply with text."""
    # Get the highest resolution version of the photo
    photo = update.message.photo[-1]

    # Let the user know we're working on it
    processing_msg = await update.message.reply_text(
        "Got it! Processing your image... This may take a few minutes."
    )

    tmp_path = os.path.join(TMP_DIR, f"{photo.file_unique_id}.jpg")

    try:
        # Download the photo to a temp file
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(tmp_path)

        logger.info("Downloaded photo to %s", tmp_path)

        # Run OCR
        text = extract_text(tmp_path)

        if not text or not text.strip():
            await processing_msg.edit_text(
                "I couldn't find any text in this image. "
                "Try sending a clearer photo with better lighting."
            )
            return

        # Telegram messages have a 4096 char limit
        if len(text) > 4000:
            # Send in chunks
            chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
            await processing_msg.edit_text(chunks[0])
            for chunk in chunks[1:]:
                await update.message.reply_text(chunk)
        else:
            await processing_msg.edit_text(text)

    except Exception:
        logger.exception("Error processing photo")
        await processing_msg.edit_text(
            "Sorry, something went wrong while processing your image. "
            "Please try again with a different photo."
        )
    finally:
        # Clean up the temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photos sent as documents (uncompressed)."""
    document = update.message.document

    if not document.mime_type or not document.mime_type.startswith("image/"):
        await update.message.reply_text(
            "I can only process images. Please send a photo of handwritten text."
        )
        return

    processing_msg = await update.message.reply_text(
        "Got it! Processing your image... This may take a few minutes."
    )

    tmp_path = os.path.join(TMP_DIR, f"{document.file_unique_id}_{document.file_name}")

    try:
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(tmp_path)

        logger.info("Downloaded document to %s", tmp_path)

        text = extract_text(tmp_path)

        if not text or not text.strip():
            await processing_msg.edit_text(
                "I couldn't find any text in this image. "
                "Try sending a clearer photo with better lighting."
            )
            return

        if len(text) > 4000:
            chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
            await processing_msg.edit_text(chunks[0])
            for chunk in chunks[1:]:
                await update.message.reply_text(chunk)
        else:
            await processing_msg.edit_text(text)

    except Exception:
        logger.exception("Error processing document")
        await processing_msg.edit_text(
            "Sorry, something went wrong while processing your image. Please try again."
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unexpected text messages."""
    await update.message.reply_text(
        "Send me a photo of handwritten text and I'll transcribe it! "
        "Use /help for tips on getting the best results."
    )


def main():
    """Start the bot."""
    logger.info("Connecting to OCR service...")
    warmup_client()
    logger.info("Connected. Starting bot...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Photo handler -- this is the main one
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Document handler -- for uncompressed images sent as files
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Text handler -- gentle redirect
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
