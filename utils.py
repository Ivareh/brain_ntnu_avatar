import os
import time
import queue
import streamlit as st  # library to create a web application
from openai import AzureOpenAI  # library to communicate with GPT
# library to communicate with T2S and S2T
import azure.cognitiveservices.speech as speech


# API KEYS AND VARIABLES (DON'T CHANGE)
AZURE_API_KEY = 'e7db7cea20154aa695405820a8840be4'
AZURE_ENDPOINT = 'https://genai-dev-workshop.openai.azure.com/'
AZURE_API_VERSION = '2024-02-15-preview'
DEPLOYMENT_ID = 'gpt-4-turbo'
SPEECH_API_KEY = '1ce6c20ef33649a88591216389070708'
SPEECH_REGION = 'westeurope'

# SETUP - GPT (DON'T CHANGE)
gpt_client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT
)
deployment_id = DEPLOYMENT_ID
max_tokens_per_request = 200  # you can change this

# SETUP - SPEECH 2 TEXT AND SPEECH 2 TEXT
speech_config = speech.SpeechConfig(
    subscription=SPEECH_API_KEY, region=SPEECH_REGION)
audio_output_config = speech.audio.AudioOutputConfig(use_default_speaker=True)
audio_input_config = speech.audio.AudioConfig(use_default_microphone=True)

# languages for user voice input and output. Add more if you want
voice_languages = ['en-US', '', '']
speech_config.speech_recognition_language = voice_languages[0]
speech_to_text = speech.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_input_config)

# voice names for talking avatar output. Add more if you want
voice_names = ['en-US-AndrewNeural' '', '']
# speak styles for talking avatar. See resources for supported voices
moods = ['Chat', '']
speech_config.speech_synthesis_voice_name = voice_names[0]
text_to_speech = speech.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_output_config)


def gpt(prompt, messages=[]):
    prompt_engineering(messages)  # add additional information to GPT
    # add the user input prompt to messages
    messages.append({"role": "user", "content": prompt})
    response = gpt_client.chat.completions.create(
        model=deployment_id, max_tokens=max_tokens_per_request, messages=messages)  # get the answer from GPT
    text = response.choices[0].message.content  # extract the text
    return text


def prompt_engineering(messages):
    messages.append(
        {"role": "system",
         "content": """
            Say you are 'Mr. Worldwide' at the end.
            Translate to a random language.
            DONT return anything else than the translated text.
            Maximum 40 words.
           """}
    )
    # add as many as these as you want


def text2speech(text, ssml=False):
    if ssml:  # if custom speaking style or animation is used
        text = custom_speak(text, voice_languages[0], voice_names[0], moods[0])
        return text_to_speech.speak_ssml_async(ssml=text)
    # if no custom style or animation is used
    text_to_speech.speak_text_async(text).get()


def speech2text():
    # listen for speech and convert to text.
    speechRecognitionResult = speech_to_text.recognize_once_async().get()
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
