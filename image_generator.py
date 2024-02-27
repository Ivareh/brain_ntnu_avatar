import os
import requests
import json
import streamlit as st # library to create a web application
from openai import AzureOpenAI # library to communicate with GPT

### API KEYS AND VARIABLES (DON'T CHANGE)
AZURE_API_KEY='e7db7cea20154aa695405820a8840be4'
AZURE_ENDPOINT='https://genai-dev-workshop.openai.azure.com/'
AZURE_API_VERSION='2024-02-15-preview'
IMAGE_DEPLOYMENT_ID='dalle-e-3'

def image_generation(image_prompt, file_name):
    client = AzureOpenAI(
        api_version=AZURE_API_VERSION,  
        api_key=AZURE_API_KEY,  
        azure_endpoint=AZURE_ENDPOINT
    )

    result = client.images.generate(
        model=IMAGE_DEPLOYMENT_ID, # the name of your DALL-E 3 deployment
        prompt=image_prompt,
        n=1
    )

    json_response = json.loads(result.model_dump_json())

    # Initialize the image path (note the filetype should be png)
    image_path = os.path.join('images/', file_name)

    # Retrieve the generated image
    image_url = json_response["data"][0]["url"]  # extract image URL from response
    generated_image = requests.get(image_url).content  # download the image
    with open(image_path, "wb") as image_file:
        image_file.write(generated_image)


### WEB APPLICATION

st.set_page_config(layout="wide")

title_placeholder = st.empty()
title_placeholder.title("Welcome to BRAIN x KPMG AI Workshop")

leftColumn, centerColumn, rightColumn = st.columns(3)

with centerColumn:
    text_input_placeholder = st.empty()
    text_placeholder = st.empty()
    image_prompt = text_input_placeholder.text_input('Generate an image here')
    if image_prompt:
        text_placeholder.write('Image is generating...')
        file_name = 'generated_image.png'
        image_generation(image_prompt, file_name)
        text_placeholder.write('')
        st.image('images/' + file_name)
    