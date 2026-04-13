"""
OCR module using Chandra OCR 2 via HuggingFace Spaces.

Calls the public victor/chandra-ocr-2 Space (ZeroGPU) through
the Gradio client API. No local model or GPU needed.
"""

import logging
from pathlib import Path

from gradio_client import Client, handle_file

from config import HF_SPACE_ID

logger = logging.getLogger(__name__)

# Reusable client -- created once, reused for all requests
_client = None


def init_client():
    """Initialize the Gradio client for the HF Space."""
    global _client

    if _client is not None:
        logger.info("Client already initialized, skipping.")
        return

    logger.info("Connecting to HuggingFace Space: %s", HF_SPACE_ID)
    _client = Client(HF_SPACE_ID)
    logger.info("Connected successfully.")


def extract_text(image_path: str | Path) -> str:
    """Extract text from an image using the HF Space API.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text as a string (markdown formatted).

    Raises:
        RuntimeError: If the client hasn't been initialized yet.
    """
    if _client is None:
        raise RuntimeError("Client not initialized. Call init_client() first.")

    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    logger.info("Sending image to HF Space: %s", image_path.name)

    # The Space's run_ocr function takes:
    #   image (PIL Image), prompt_type (str), max_tokens (int)
    # and returns:
    #   (markdown_text, raw_html)
    result = _client.predict(
        image=handle_file(str(image_path)),
        prompt_type="ocr_layout",
        max_tokens=12384,
        api_name="/run_ocr",
    )

    # result is a tuple: (markdown_text, raw_html)
    markdown = result[0] if isinstance(result, (list, tuple)) else result

    logger.info(
        "OCR complete for: %s (%d chars extracted)", image_path.name, len(markdown)
    )
    return markdown
