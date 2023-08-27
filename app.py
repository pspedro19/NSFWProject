# Import necessary libraries
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from io import BytesIO
import os
import subprocess
from google_drive_downloader import GoogleDriveDownloader as gdd
from clip_interrogator import Config, Interrogator

# Initialize the FastAPI app
app = FastAPI()

# Define a function to set up the required dependencies
def setup():
    install_cmds = [
        ['pip', 'install', 'gradio'],
        ['pip', 'install', 'open_clip_torch'],
        ['pip', 'install', 'clip-interrogator'],
    ]
    for cmd in install_cmds:
        print(subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8'))

# Call the setup function to install the required dependencies
setup()

# Initialize the Clip Interrogator configuration
config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

# Define a function to process images and generate prompts
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

# Define a route to process videos
@app.post("/api/process_videos/")
async def process_videos(folder_info: dict):
    try:
        # Extract the folder URL from the request
        folder_url = folder_info.get("folder_url")
        if not folder_url:
            raise HTTPException(status_code=400, detail="Folder URL is missing in the request")

        # List files in the Google Drive folder
        files = gdd.list_files(folder_url=folder_url)

        # Process the files and return results
        results = []
        for file_info in files:
            file_id = file_info["id"]
            file_name = file_info["name"]
            # Download file data from Google Drive
            file_path = os.path.join('files', file_name)
            gdd.download_file_from_google_drive(file_id=file_id, dest_path=file_path)

            # Process file and get its analysis results
            with open(file_path, "rb") as file:
                file_data = file.read()
            file_stream = BytesIO(file_data)
            file_data = Image.open(file_stream)
            prompt = image_to_prompt(file_data, mode="best")  # Modify the mode as needed
            analysis_result = {"file": file_name, "prompt": prompt}
            results.append(analysis_result)

        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Run the app using Gunicorn on port 4000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
