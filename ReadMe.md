# dubAI

A voice-cloning text-to-speech pipeline that translates input text and generates speech in the cloned voice of a reference speaker, using Coqui XTTSv2.

## How It Works

dubAI runs as two separate services:

1. **Kaggle GPU Server** (`dubai_server.py`) — loads the XTTSv2 model on a Kaggle GPU instance, exposes a `/inference` endpoint, and tunnels it to the internet via ngrok. Handles translation and the actual voice-cloned speech synthesis.
2. **Local Client** (`main.py`) — a lightweight FastAPI server that runs locally, exposes a `/generate-dub/` endpoint, and forwards requests to the Kaggle server.

```
User --> Local FastAPI (main.py) --> ngrok tunnel --> Kaggle GPU Server (dubai_server.py) --> XTTSv2
```

This split exists because XTTSv2 needs GPU acceleration to run at a usable speed, and Kaggle provides free GPU access without requiring a dedicated GPU machine locally.

## Features

- Accepts an English (or any source language) text script.
- Translates the text into a target language (currently tested with Hindi, `hi`).
- Clones the voice from a short reference `.wav` clip and generates speech in the translated text, in that cloned voice.

## Setup

### Kaggle Side

1. Open a new Kaggle notebook with GPU enabled.
2. Add an `NGROK_AUTH_TOKEN` secret under **Add-ons → Secrets** (get a free token from [ngrok.com](https://ngrok.com)).
3. Install dependencies:
   ```bash
   /usr/bin/python3.10 -m pip install --ignore-installed blinker -r kaggle_requirements.txt
   ```
4. Run `dubai_server.py`:
   ```bash
   /usr/bin/python3.10 dubai_server.py
   ```
5. Copy the printed `🚀 PUBLIC KAGGLE URL: ...` — this changes every time the notebook restarts.

### Local Side

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Update `KAGGLE_URL` in `main.py` with the ngrok URL from the Kaggle step.
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Usage

```bash
curl -X POST "http://127.0.0.1:8000/generate-dub/" \
  -F "text=Hi, how are you?" \
  -F "target_language=hi" \
  -F "reference_audio=@reference.wav" \
  --output result.wav
```

- `text` — the script to translate and synthesize.
- `target_language` — target language code (e.g. `hi` for Hindi).
- `reference_audio` — a short (~8-10 second), clean `.wav` clip of the voice to clone. The content of this clip does not need to match `text`; only the voice characteristics are used.

## Known Constraints

- **Supported languages**: XTTSv2 officially supports a fixed set of languages (`en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko, hi`). Languages outside this list (e.g. Kannada, Tamil, Telugu) are not natively supported and will either error or produce inaccurate pronunciation.
- **Dependency versions are pinned deliberately**: `transformers==4.40.2` and `torch==2.4.1`/`torchaudio==2.4.1` are required for compatibility with `TTS==0.22.0`. Newer versions of either library break XTTSv2 loading (`BeamSearchScorer` import error, or `torch.load` weights-only deserialization errors).
- **Kaggle ngrok URL is not persistent** — it changes on every notebook restart and must be manually updated in `main.py`.
- **License**: XTTSv2 is distributed under Coqui's CPML (non-commercial) license. This project is for educational/research use only.

## Roadmap

- [ ] Expand language coverage and evaluate native support for more Indian regional languages via alternate models (e.g. AI4Bharat Indic-TTS).
- [ ] Containerize the Kaggle-side server for easier redeployment.
- [ ] Add automated tests for the translation and synthesis pipeline.