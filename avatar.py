from utils import gpt, prompt_engineering, text2speech, speech2text, custom_speak
import streamlit as st

ANIMATE = False  # set to True if you want to animate the avatar

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
            