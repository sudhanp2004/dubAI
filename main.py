import os
import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="dubAI_Local_Client")

# Allow the frontend (index.html, opened directly in a browser or served
# from a different origin) to call this API. Locked to localhost origins;
# widen this list only if you actually serve the frontend from elsewhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://127.0.0.1",
        "null",  # covers index.html opened directly via file:// in some browsers
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace with the public Kaggle ngrok URL printed when dubai_server.py starts.
# This changes every time the Kaggle notebook restarts.
KAGGLE_URL = "https://flatbed-flammable-handlebar.ngrok-free.dev"

os.makedirs("temp_storage", exist_ok=True)


@app.post("/generate-dub/")
async def generate_dub(
    text: str = Form(...),
    target_language: str = Form(...),
    reference_audio: UploadFile = File(...)
):
    try:
        files = {
            "audio_file": (reference_audio.filename, reference_audio.file, reference_audio.content_type)
        }
        data = {
            "text": text,
            "target_language": target_language
        }

        response = requests.post(f"{KAGGLE_URL}/inference", data=data, files=files, timeout=120)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Kaggle server error ({response.status_code}): {response.text}"
            )

        # Save returned audio bytes to disk and return as a real .wav file,
        # not JSON — the Kaggle server streams back raw audio bytes.
        out_path = os.path.join("temp_storage", "dubbed_output.wav")
        with open(out_path, "wb") as f:
            f.write(response.content)

        return FileResponse(out_path, media_type="audio/wav", filename="dubbed_output.wav")

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach Kaggle server at {KAGGLE_URL}. Is the notebook running and the ngrok URL current?"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Kaggle server timed out generating audio.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Simple reachability check used by the frontend's connection indicator."""
    return {"status": "ok", "kaggle_url": KAGGLE_URL}