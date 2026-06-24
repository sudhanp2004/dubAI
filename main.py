import os
import requests
from fastapi import FastAPI, File, UploadFile, Form, HTTPException

app = FastAPI(title="dubAI_Local_Client")

# Replace with the 🚀 PUBLIC KAGGLE URL you generated in the previous step
KAGGLE_URL = "https://flatbed-flammable-handlebar.ngrok-free.dev"

os.makedirs("temp_storage", exist_ok=True)

@app.post("/generate-dub/")
async def generate_dub(
    text: str = Form(...),
    target_language: str = Form(...),
    reference_audio: UploadFile = File(...)
):
    try:
        # 1. Prepare payload for Kaggle
        files = {
            "audio_file": (reference_audio.filename, reference_audio.file, reference_audio.content_type)
        }
        data = {
            "text": text, 
            "target_language": target_language
        }
        
        # 2. Forward request to Kaggle Server
        response = requests.post(f"{KAGGLE_URL}/inference", data=data, files=files)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Kaggle server error: {response.text}")
            
        # 3. Return the Kaggle response to the user
        return response.json()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))