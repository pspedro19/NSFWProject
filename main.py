from fastapi import FastAPI
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import os
import subprocess
from google_drive_downloader import GoogleDriveDownloader as gdd
from clip_interrogator import Config, Interrogator

app = FastAPI()

def setup():
    install_cmds = [
        ['pip', 'install', 'gradio'],
        ['pip', 'install', 'open_clip_torch'],
        ['pip', 'install', 'clip-interrogator'],
    ]
    for cmd in install_cmds:
        print(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8'))

setup()

config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

def image_to_prompt(image, mode):
    ci.config.chunk_size = 2048 if ci.config.clip_model_name == "ViT-L-14/openai" else 1024
    ci.config.flavor_intermediate_count = 2048 if ci.config.clip_model_name == "ViT-L-14/openai" else 1024
    image = image.convert('RGB')
    if mode == 'best':
        return ci.interrogate(image)
    elif mode == 'classic':
        return ci.interrogate_classic(image)
    elif mode == 'fast':
        return ci.interrogate_fast(image)
    elif mode == 'negative':
        return ci.interrogate_negative(image)

@app.post("/api/process_videos/")
async def process_videos():
    try:
        # Replace with the Google Drive folder URL
        folder_url = "https://drive.google.com/drive/folders/1N6KpWfYhOt_s2I6jGEIKiERLMY2J8Sqa?usp=sharing"

        # Extract the folder ID from the URL
        folder_id = folder_url.split("/")[5].split("?")[0]

        # List video filenames in the local "videos" directory
        videos_folder = 'videos'
        video_filenames = os.listdir(videos_folder)

        # Process the videos and return results
        results = []
        for video_filename in video_filenames:
            # Process video and get its analysis results
            video_path = os.path.join(videos_folder, video_filename)
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
            video_stream = BytesIO(video_data)
            video_image = Image.open(video_stream)
            prompt = image_to_prompt(video_image, mode="best")  # Modify the mode as needed
            analysis_result = {"video": video_filename, "prompt": prompt}
            results.append(analysis_result)

        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

