"""
OCR module using Chandra OCR 2 via HuggingFace Spaces.

Calls the public victor/chandra-ocr-2 Space (ZeroGPU) through
the Gradio client API. No local model or GPU needed.
"""

import logging
from pathlib import Path

from gradio_client import Client, handle_file

from config import HF_SPACE_ID, HF_TOKEN

logger = logging.getLogger(__name__)


def _create_client() -> Client:
    """Create a fresh Gradio client for the HF Space.

    A new client is created per request to avoid accumulating
    session state that counts against ZeroGPU quota.
    """
    logger.info("Connecting to HuggingFace Space: %s", HF_SPACE_ID)
    client = Client(HF_SPACE_ID, token=HF_TOKEN)
    logger.info("Connected successfully.")
    return client


def warmup_client():
    """Test that we can connect to the HF Space at startup.

    This is a connectivity check only -- the client is not reused.
    """
    client = _create_client()
    del client
    logger.info("Warmup complete -- Space is reachable.")


def extract_text(image_path: str | Path) -> str:
    """Extract text from an image using the HF Space API.

    Creates a fresh client for each call to avoid ZeroGPU session
    quota accumulation.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text as a string (markdown formatted).
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    logger.info("Sending image to HF Space: %s", image_path.name)

    client = _create_client()

    # The Space's run_ocr function takes:
    #   image (PIL Image), prompt_type (str), max_tokens (int)
    # and returns:
    #   (markdown_text, raw_html)
    result = client.predict(
        image=handle_file(str(image_path)),
        prompt_type="ocr_layout",
        max_tokens=4096,
        api_name="/run_ocr",
    )

    # result is a tuple: (markdown_text, raw_html)
    markdown = result[0] if isinstance(result, (list, tuple)) else result

    logger.info(
        "OCR complete for: %s (%d chars extracted)", image_path.name, len(markdown)
    )
    return markdown
