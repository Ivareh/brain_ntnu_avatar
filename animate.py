### ANIMATION SETUP
import time
import queue
import streamlit as st # library to create a web application

ANIMATE = True
time_offset_delay = 0.015
speech_start_time = 1.5
mouth_closed_threshold = 0.5
image_width = 512
max_subtitle_length = 70
expression_queue = queue.Queue()
spoken_word_queue = queue.Queue()
animation_path = "images/"
sentence_dividers = [".", "!", "?", ";", "。", "！", "？", "；", "\n" ]

def viseme(expression):
    if expression.viseme_id:
        expression_queue.put(((expression.audio_offset / 10000000)+speech_start_time, expression.viseme_id))
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

### WEB APPLICATION

if ANIMATE:
    estimated_talking_time = estimated_speech_time(text)
    print(estimated_talking_time)
    text2speech(text, ssml=True)
    start_time = time.time()
    timer = 0
    prev_time = 0
    expression_queue.put((speech_start_time,1))
    full_sentence = ""
    
    while expression_queue.queue or timer<estimated_talking_time:
        timer = time.time() - start_time
        if expression_queue.queue:
            text = expression_queue.get()

            if spoken_word_queue.queue:
                word = spoken_word_queue.get()
                if word in sentence_dividers:
                    full_sentence += (word)
                else:
                    full_sentence += (word + " " or "")
                text_placeholder.markdown(f'<p style="text-align: center";>{full_sentence}</p>', unsafe_allow_html=True)
                if word in sentence_dividers or len(full_sentence) > max_subtitle_length:
                    full_sentence = ""


            curr_time = text[0] - prev_time
            prev_time = text[0]
            if curr_time > time_offset_delay:
                if curr_time > mouth_closed_threshold:
                    image_placeholder.image(animation_path + "0.jpg", width=image_width)
                time.sleep(curr_time-time_offset_delay)
            else:
                time.sleep(curr_time) 

            print(text)
            image_placeholder.image(animation_path + f"{text[1]}.jpg", width=image_width)
        else: 
            image_placeholder.image(animation_path + "0.jpg", width=image_width)
    print('done')
    image_placeholder.image(animation_path + "22.jpg", width=image_width)
    text_placeholder.markdown(" ")
else:
    text2speech(text)
