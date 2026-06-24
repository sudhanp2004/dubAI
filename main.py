import os
import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI(title="dubAI_Local_Client")

KAGGLE_URL = "https://flatbed-flammable-handlebar.ngrok-free.dev"  # update each Kaggle run

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
        data = {"text": text, "target_language": target_language}

        response = requests.post(f"{KAGGLE_URL}/inference", data=data, files=files)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Kaggle server error: {response.text}")

        # Save returned audio bytes to disk
        out_path = os.path.join("temp_storage", "dubbed_output.wav")
        with open(out_path, "wb") as f:
            f.write(response.content)

        return FileResponse(out_path, media_type="audio/wav", filename="dubbed_output.wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))