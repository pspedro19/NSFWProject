from fastapi import FastAPI, File, UploadFile, Form
from typing import List
import json
import uvicorn
import shutil
from pathlib import Path
import random
from moviepy.editor import VideoFileClip
from PIL import Image
from clip_interrogator import Config, Interrogator
import os
import requests
# Configurar el modelo de IA
config = Config()
config.clip_model_name = 'ViT-L-14/openai'
config.caption_model_name = 'blip-large'
ci = Interrogator(config)

app = FastAPI()

async def extract_screenshots(video_path: Path, num_screenshots: int = 1):
    clip = VideoFileClip(str(video_path))
    duration = clip.duration
    text_list = []

    for i in range(num_screenshots):
        time = random.uniform(0, duration)
        screenshot_path = Path(f"{video_path.stem}screenshot{i + 1}.png")
        clip.save_frame(screenshot_path, t=time)

        # Convertir la imagen a texto usando tu modelo
        image = Image.open(screenshot_path).convert('RGB')
        text = ci.interrogate(image)  # Utilizando tu función 'interrogate'
        text_list.append(text)

    return text_list

@app.post("/uploadvideos/")
async def upload_videos(
    files: List[UploadFile] = File(...),
    studio: str = Form(...),
    pornstars: str = Form(...),
    keywords: str = Form(...)
):
    file_names = []
    texts = {}

    for file in files:
        file_names.append(file.filename)

        # Crear un Path para el archivo en el directorio raíz
        path = Path(file.filename)

        # Escribir el archivo en el sistema de archivos
        with path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extraer 5 capturas de pantalla aleatorias del video y convertirlas a texto
        text_list = await extract_screenshots(path)
        texts[file.filename]= text_list
    texto = texts[file.filename][0]
    prompt = "Give me a coherence video description for a sex porn video use explicit words the name of the porn model and context to make up the video descriptions, souds dirty and use all vocabulary related for NFSW for sex and porn escenes"
    prompt = prompt + "############  use this context to create the description, use only the most important words and make up the porn video description: " +  texto + " ################## Pornstarname:"+ pornstars + "###################### Include in the description the following key words:" + keywords 
    HOST = 'localhost:5000'
    URI = f'http://{HOST}/api/v1/chat'
    history = {'internal': [], 'visible': []}
    request = {
        'user_input': prompt,
        'max_new_tokens': 250,
        'auto_max_new_tokens': False,
        'max_tokens_second': 0,
        'history': history,
        'mode': 'instruct',  # Valid options: 'chat', 'chat-instruct', 'instruct'
        'character': 'Example',
        'instruction_template': 'Vicuna-v1.1',  # Will get autodetected if unset
        'your_name': 'You',

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'None',
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'epsilon_cutoff': 0,  # In units of 1e-4
        'eta_cutoff': 0,  # In units of 1e-4
        'tfs': 1,
        'top_a': 0,
        'repetition_penalty': 1.18,
        'repetition_penalty_range': 0,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'mirostat_mode': 0,
        'mirostat_tau': 5,
        'mirostat_eta': 0.1,
        'guidance_scale': 1,
        'negative_prompt': '',

        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': True,
        'stopping_strings': []
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['history']

    result = response.json()['results'][0]['history']
    otro = print(json.dumps(result, indent=4))
    otro = str(otro)
    print(json.dumps(result, indent=4))
    print(prompt)
    print(str(result))
    result = str(result)
    return { "Description": result}

if name == "main":
    uvicorn.run(app, host="0.0.0.0", port=4000)