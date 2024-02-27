import os
import time
import queue
import streamlit as st # library to create a web application
from openai import AzureOpenAI # library to communicate with GPT
import azure.cognitiveservices.speech as speech # library to communicate with T2S and S2T


### API KEYS AND VARIABLES (DON'T CHANGE)
AZURE_API_KEY='e7db7cea20154aa695405820a8840be4'
AZURE_ENDPOINT='https://genai-dev-workshop.openai.azure.com/'
AZURE_API_VERSION='2024-02-15-preview'
DEPLOYMENT_ID='gpt-4-turbo'
SPEECH_API_KEY='1ce6c20ef33649a88591216389070708'
SPEECH_REGION='westeurope'

### SETUP - GPT (DON'T CHANGE)
gpt_client = AzureOpenAI(
    api_key=AZURE_API_KEY,  
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
    )
deployment_id = DEPLOYMENT_ID
max_tokens_per_request = 200 # you can change this

### SETUP - SPEECH 2 TEXT AND SPEECH 2 TEXT
speech_config = speech.SpeechConfig(subscription=SPEECH_API_KEY, region=SPEECH_REGION)
audio_output_config = speech.audio.AudioOutputConfig(use_default_speaker=True)
audio_input_config = speech.audio.AudioConfig(use_default_microphone=True)

voice_languages = ['en-US', '', ''] # languages for user voice input and output. Add more if you want
speech_config.speech_recognition_language = voice_languages[0]
speech_to_text = speech.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input_config)

voice_names = ['en-US-AndrewNeural' '', ''] # voice names for talking avatar output. Add more if you want
moods = ['Chat', ''] # speak styles for talking avatar. See resources for supported voices 
speech_config.speech_synthesis_voice_name = voice_names[0] 
text_to_speech = speech.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)


### ANIMATION SETUP
# if you want to animate the avatar, copy the code from animate.py to here
ANIMATE = False


### AVATAR ELEMENTS

def gpt(prompt, messages=[]):
    prompt_engineering(messages) # add additional information to GPT
    messages.append({"role": "user", "content": prompt}) # add the user input prompt to messages
    response = gpt_client.chat.completions.create(model=deployment_id, max_tokens=max_tokens_per_request, messages=messages) # get the answer from GPT
    text = response.choices[0].message.content # extract the text
    return text

def prompt_engineering(messages): 
    messages.append(
        {"role": "system", 
         "content": "Answer in maximum 40 words."}
        )
    # add as many as these as you want

def text2speech(text, ssml = False):
    if ssml: # if custom speaking style or animation is used
        text = custom_speak(text, voice_languages[0], voice_names[0], moods[0])
        return text_to_speech.speak_ssml_async(ssml=text)
    text_to_speech.speak_text_async(text).get() # if no custom style or animation is used
        
def speech2text():
    speechRecognitionResult = speech_to_text.recognize_once_async().get() # listen for speech and convert to text.
    return speechRecognitionResult.text

def custom_speak(text, language, voice_name, mood):
    ssml_text = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="{language}">
                    <voice name="{voice_name}">
                        <mstts:viseme type="redlips_front"/>
                        <mstts:express-as style="{mood}">
                            {text}
                        </mstts:express-as>
                    </voice>
                </speak>
            """
    return ssml_text


### WEB APPLICATION

st.set_page_config(layout="wide")

title_placeholder = st.empty()
title_placeholder.title("Mr. Worldwide")


subtitle_placeholder = st.empty()
#subtitle_placeholder.write("You are running the code. Great start, now create your AI avatar!")

if "messages" not in st.session_state: # initialize chat history
    st.session_state.messages = []

leftColumn, centerColumn, rightColumn = st.columns(3)

with leftColumn:
    text_input_placeholder = st.empty()
    text_placeholder = st.empty()
    

with centerColumn:
    image_placeholder = st.empty()
    image_placeholder.image("images/avatar.png")
    chat_input_placeholder = st.empty()
    voice_input_placeholder = st.empty()


with rightColumn:
    with st.container(height=800, border=False):
        for message in st.session_state.messages:
            avatar = 'images/avatar.png' if message["role"] == 'assistant' else None
            if message['role'] == 'user' or message['role'] == 'assistant':
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
        prompt = chat_input_placeholder.chat_input('Ask me something')
        if voice_input_placeholder.button('Press here and speak a question'):
            prompt = "" # add speech2text here if you want
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar = 'images/avatar.png'):
                message = st.empty()
                message.markdown("...")
                messages = st.session_state.messages
                text = gpt(prompt=prompt, messages=messages)  # this just repeats what you input
                message.markdown(text)
                if not ANIMATE:
                    pass # add text to speech here and remove 'pass'
            st.session_state.messages.append({"role": "assistant", "content": text})

            if ANIMATE:
                pass # add animation and remove 'pass'
            