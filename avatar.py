from utils import gpt, prompt_engineering, text2speech, speech2text, custom_speak, text_to_speech
import streamlit as st
import queue
import time


# ANIMATION SETUP
ANIMATE = True
time_offset_delay = 0.015
speech_start_time = 1.5
mouth_closed_threshold = 0.5
image_width = 512
max_subtitle_length = 70
expression_queue = queue.Queue()
spoken_word_queue = queue.Queue()
animation_path = "images/"
sentence_dividers = [".", "!", "?", ";", "。", "！", "？", "；", "\n"]


def viseme(expression):
    if expression.viseme_id:
        expression_queue.put(
            ((expression.audio_offset / 10000000)+speech_start_time, expression.viseme_id))


def viseme_word(spoken_word):
    spoken_word_queue.put(spoken_word.text)


def viseme_status(status):
    print(status.result.reason)


text_to_speech.viseme_received.connect(viseme)
text_to_speech.synthesis_word_boundary.connect(viseme_word)
text_to_speech.synthesis_started.connect(viseme_status)
text_to_speech.synthesis_completed.connect(viseme_status)


def estimated_speech_time(text):
    words_per_minute_no = 110
    words_per_minute_en = 130
    words = len(text.split())
    minutes = words / words_per_minute_en
    seconds = minutes * 60
    return seconds

st.set_page_config(layout="wide")

title_placeholder = st.empty()
title_placeholder.title("Mr. Worldwide")


subtitle_placeholder = st.empty()
# subtitle_placeholder.write("You are running the code. Great start, now create your AI avatar!")

if "messages" not in st.session_state:  # initialize chat history
    st.session_state.messages = []

leftColumn, centerColumn, rightColumn = st.columns(3)

with leftColumn:
    text_input_placeholder = st.empty()
    text_placeholder = st.empty()


with centerColumn:
    image_placeholder = st.empty()
    image_placeholder.image("images/1.png", width=400)
    chat_input_placeholder = st.empty()
    voice_input_placeholder = st.empty()


with rightColumn:
    with st.container(height=800, border=False):
        for message in st.session_state.messages:
            avatar = 'images/1.png' if message["role"] == 'assistant' else None
            if message['role'] == 'user' or message['role'] == 'assistant':
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])
        prompt = chat_input_placeholder.chat_input('Ask me something')
        if voice_input_placeholder.button('Press here and speak a question'):
            prompt = speech2text()  # add speech2text here if you want
        if prompt:
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar='images/1.png'):
                message = st.empty()
                message.markdown("...")
                messages = st.session_state.messages
                # this just repeats what you input
                text = gpt(prompt=prompt, messages=messages)
                message.markdown(text)
                if not ANIMATE:
                    text2speech()  # add text to speech here and remove 'pass'
            st.session_state.messages.append(
                {"role": "assistant", "content": text})

            if ANIMATE:
                estimated_talking_time = estimated_speech_time(text)
                print(estimated_talking_time)
                text2speech(text, ssml=True)
                start_time = time.time()
                timer = 0
                prev_time = 0
                expression_queue.put((speech_start_time, 1))
                full_sentence = ""

                while expression_queue.queue or timer < estimated_talking_time:
                    timer = time.time() - start_time
                    if expression_queue.queue:
                        text = expression_queue.get()

                        if spoken_word_queue.queue:
                            word = spoken_word_queue.get()
                            if word in sentence_dividers:
                                full_sentence += (word)
                            else:
                                full_sentence += (word + " " or "")
                            text_placeholder.markdown(
                                f'<p style="text-align: center";>{full_sentence}</p>', unsafe_allow_html=True)
                            if word in sentence_dividers or len(full_sentence) > max_subtitle_length:
                                full_sentence = ""

                        curr_time = text[0] - prev_time
                        prev_time = text[0]
                        if curr_time > time_offset_delay:
                            if curr_time > mouth_closed_threshold:
                                image_placeholder.image(
                                    animation_path + "0.png", width=400)
                            time.sleep(curr_time-time_offset_delay)
                        else:
                            time.sleep(curr_time)

                        image_placeholder.image(
                            animation_path + f"1.png", width=400)
                    else:
                        image_placeholder.image(
                            animation_path + "0.png", width=400)
                print('done')
                image_placeholder.image(animation_path + "1.png", width=400)
                text_placeholder.markdown(" ")
            else:
                text2speech(text)

