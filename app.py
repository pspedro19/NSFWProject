from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from typing import List
from io import BytesIO
import shutil
from pathlib import Path
import os
from clip_interrogator import Config, Interrogator  # Ensure this package is installed

# Initialize the FastAPI app
app = FastAPI()

# Initialize the Clip Interrogator configuration and Interrogator
config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

# Directory to store uploaded videos
video_directory = "uploaded_videos"

# Create the directory if it doesn't exist
Path(video_directory).mkdir(parents=True, exist_ok=True)

# Function to process images and generate prompts
def image_to_prompt(image, mode):
    prompt = ci.get_prompt_from_image(image, mode=mode)
    return prompt

# Function to process videos and generate prompts
def video_to_prompt(video_path, mode):
    with open(video_path, "rb") as video_file:
        video_data = video_file.read()
    video_stream = BytesIO(video_data)
    video_image = Image.open(video_stream)
    prompt = image_to_prompt(video_image, mode=mode)
    return prompt

# Endpoint to upload videos
@app.post("/uploadvideos/")
async def upload_videos(files: List[UploadFile] = File(...)):
    file_names = []
    for file in files:
        file_names.append(file.filename)
        path = Path(video_directory) / file.filename
        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return {"filenames": file_names}

# Endpoint to process uploaded videos
@app.post("/api/process_videos/")
async def process_videos():
    try:
        video_filenames = list(Path(video_directory).glob("*.mp4"))  # Scan for .mp4 files in the upload directory
        results = []
        for video_filename in video_filenames:
            try:
                prompt = video_to_prompt(video_filename, mode="best")
                analysis_result = {"video": video_filename.name, "prompt": prompt}
                results.append(analysis_result)
            except Exception as e:
                results.append({"video": video_filename.name, "error": str(e)})
        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
