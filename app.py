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
    prompt = "Give me a coherence video description for a sex porn video use explicit words the name of the porn model and context to make up the video descriptions, souds dirty and use all vocabulary related for NFSW for sex and porn escenes The title and description must not contain the whole sentences in uppercase, The title and description must not contain any symmbol @_#$%^&*()<>/\|}{][~:;, The title and description must not contain studio name as well as the words 'episode','scene','chapter', The title and description MUST ONLY contain pronouns and verbs in the third person singular, The title and description must not contain an ellipsis, exclamation point, or question mark"
    prompt = prompt + "############  use this context to create the description, use only the most important words and make up the porn video description: " +  texto + " ################## Pornstarname:"+ pornstars + "###################### Include in the description the following key words:" + keywords + "always include a title and description using colon simbols after the tilte and after the description like this title: description after the title make up the title and after the description make up the description"
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

    # Your 'result' string
    #result = "{'internal': [['Este anexo muestra una cronología de los eventos más relevantes de la historia de las personas LGTB en la república de Islandia. La historia de las personas lesbianas, gais, bisexuales y transgénero (LGBT) en Islandia se diferencia de la de otros países escandinavos por la baja visibilidad que tuvieron hasta mediados del siglo xx. Esto se debió a que la población de Islandia era mucho menor a la de sus análogos nórdicos y que durante gran parte de su historia fue principalmente una sociedad agraria.', 'visible': [['Este anexo muestra una cronología de los eventos más relevantes de la historia de las personas LGTB en la república de Islandia. La historia de las personas lesbianas, gais, bisexuales y transgénero (LGBT) en Islandia se diferencia de la de otros países escandinavos por la baja visibilidad que tuvieron hasta mediados del siglo xx. Esto se debió a que la población de Islandia era mucho menor a la de sus análogos nórdicos y que durante gran parte de su historia fue principalmente una sociedad agraria.;', 'Title: Barroco\\nDescription: El Barroco fue un período de la historia en la cultura occidental originado por una nueva forma de concebir el arte (el «estilo barroco») y que, partiendo desde diferentes contextos histórico-culturales, produjo obras en numerosos campos artísticos: literatura, arquitectura, escultura, pintura, música, ópera, danza, teatro, etc. Se manifestó principalmente en la Europa occidental, aunque debido al colonialismo también se dio en numerosas colonias de las potencias europeas, principalmente en Iberoamérica. Cronológicamente, abarcó todo el siglo xvii y principios del xviii, con mayor o menor prolongación en el tiempo dependiendo de cada país. Se suele situar entre el Manierismo y el Rococó, en una época caracterizada por fuertes disputas religiosas entre países católicos y protestantes, así como marcadas diferencias políticas entre los Estados absolutistas y los parlamentarios, donde una incipiente burguesía empezaba a poner los cimientos del capitalismo.']]}"

    # Extract the last title and description using string splitting and rfind
    last_title_idx = result.rfind('Title:')
    last_desc_idx = result.rfind('Description:')

    # Extract and clean up the last title and description
    last_title = result[last_title_idx + 6:last_desc_idx].strip("\\n").strip()
    last_desc = result[last_desc_idx + 12:].strip("\\n").strip()

    # Remove any trailing or leading spaces, and fix the escaped newline characters
    last_title = last_title.strip().replace('\\n', '\n')
    last_desc = last_desc.strip().replace('\\n', '\n')

    # Display the extracted last title and description
    print("Last Title:", last_title)
    print("Last Description:", last_desc)
    return { "Title": last_title, "Description": last_desc}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)