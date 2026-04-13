# Handwriting OCR Telegram Bot

A Telegram bot that transcribes handwritten text from photos using [Chandra OCR 2](https://huggingface.co/datalab-to/chandra-ocr-2), a state-of-the-art OCR model by Datalab with excellent handwriting support.

The bot runs OCR inference for free through a public [HuggingFace Space](https://huggingface.co/spaces/victor/chandra-ocr-2) (ZeroGPU) -- no local GPU or model download required.

## How it works

```
Phone (photo) --> Telegram --> Bot (local) --> HuggingFace Space (free GPU) --> Transcribed text
```

1. take a photo of your handwriting
2. send it to the Telegram bot
3. The bot uploads the image to a HuggingFace Space running Chandra OCR 2
4. The model extracts the text and the bot replies with the transcription

## Setup

### 1. Create a Telegram bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 2. Configure the project

```bash
git clone <your-repo-url>
cd handwriting-ocr-bot

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

Edit the `.env` file and add your tokens:

```
TELEGRAM_BOT_TOKEN=your-actual-token-from-botfather

# Optional but recommended -- gives a much higher ZeroGPU quota.
# Create a free token at https://huggingface.co/settings/tokens
# with only the "Make calls to Inference Providers" permission enabled.
HF_TOKEN=hf_your-token-here
```

### 3. Run the bot

```bash
python bot.py
```

Open Telegram, find your bot, and send it a photo of handwritten text.

## Usage

| Command  | Description                          |
|----------|--------------------------------------|
| `/start` | Welcome message                      |
| `/help`  | Tips for getting the best results    |
| *photo*  | Send any photo to get a transcription |

The bot also accepts images sent as documents (uncompressed), which may give better results for high-resolution photos.

## Project structure

```
handwriting-ocr-bot/
  bot.py              # Telegram bot -- handles messages, downloads photos, replies
  ocr.py              # OCR client -- sends images to HuggingFace Space via Gradio API
  config.py           # Configuration -- loads .env, defines constants
  requirements.txt    # Python dependencies
  .env                # Telegram bot token (not committed)
  .gitignore          # Ignores .env, venv, tmp, __pycache__
```

## Limitations

- **Cold starts**: The HuggingFace Space may take 30-60 seconds to wake up if idle. Subsequent requests are faster.
- **Queue**: If other users are using the same Space, your request may wait in a queue.
- **Availability**: The bot depends on the public `victor/chandra-ocr-2` Space. If it goes down, OCR stops working. You can [duplicate the Space](https://huggingface.co/spaces/victor/chandra-ocr-2?duplicate=true) to your own HuggingFace account for more control.
- **Bot uptime**: The bot only works while `python bot.py` is running on your machine. For always-on deployment, consider a cheap VPS or a service like Railway/Fly.io.

## Credits

- [Chandra OCR 2](https://huggingface.co/datalab-to/chandra-ocr-2) by [Datalab](https://www.datalab.to) -- the OCR model
- [victor/chandra-ocr-2 Space](https://huggingface.co/spaces/victor/chandra-ocr-2) -- the free GPU-backed inference endpoint
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) -- Telegram bot framework
- [Gradio Client](https://www.gradio.app/docs/python-client) -- API client for HuggingFace Spaces
