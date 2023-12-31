from pathlib import Path
from openai import OpenAI
import openai
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User
from api_keys import GPT_KEY, STABILITY_KEY
import shutil

create_audio = Blueprint('create_audio', __name__)

texts = {'1':"Meet George, George is a 2nd grader struggling with how to pronounce certain words. George wants to know what movies or books series you like so he can learn from you about different letter sounds! Help George learn to read by selecting the characters that correspond to each part of the word. If you can't remember who a certain character represents, ask George; he is sure to know them all.",
        '2':"What's your all-time favorite movie or book franchise? Think of epic stories like Star Wars, Harry Potter, or Marvel! Share with George!",
        '4':"George learns best by matching sounds to letters. So far he has learned four sounds /i/, /b/, /sh/, and /p/. Lets create some flash cards for each of these sounds! Below are some images generated by George, pick the one that best matches the sound displayed. If none of them are good, click regenerate to get a new set of images. Once you have clicked on an image, the flash card will be created. You can check out all created flashcards in the Progress Tracker tab.",        
        '5':'''George learns best by matching sounds to letters. So far he has learned four sounds /i/, /b/, /sh/, and /p/.
            Lets create some flash cards for each of these sounds! Below are some images generated by George, pick the one that best
            matches the sound displayed. If none of them are good, click regenerate to get a new set of images. Once you have clicked 
            on an image, the flash card will be created. You can check out all created flashcards in the Progress Tracker tab. ''',
        '6':'''Welcome to the progress tracker! This is where you can see how George (and you!) is doing with his learning. 
                    Every time you create a flashcard (matching a sound to an image), it will show up here. Once you have reviewed 
                    the flash cards hit the link below to help George practice his sounds! If you forget what sound goes with which image,
                    just click on the image below! ''',   
        '7':"Now it's time to teach George! To begin, George will ask how to pronounce a sound, and it is up to you to pick the image that corresponds to that sound. ",
        '8': "What is the first sound in the word SHIP?",
        '9': "What is the second sound in the word SHIP?",
        '10': "What is the third sound in the word SHIP?"}

client = OpenAI(api_key=GPT_KEY)
for key, text in texts.items():
    if not os.path.exists(f"website/static/sounds/{key}_sound.mp3"):
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        response.stream_to_file(f"website/static/sounds/{key}_sound.mp3")

if not os.path.exists(f"website/static/sounds/correct_sound.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Very good!"
    )
    response.stream_to_file(f"website/static/sounds/correct_sound.mp3")

if not os.path.exists(f"website/static/sounds/incorrect_sound.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Try again!"
    )
    response.stream_to_file(f"website/static/sounds/incorrect_sound.mp3")

if not os.path.exists(f"website/static/sounds/image_represent.mp3"):
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Does this image represent the sound"
    )
    response.stream_to_file(f"website/static/sounds/image_represent.mp3")

sounds_generated_path = 'website/static/sounds/generated'
os.makedirs(sounds_generated_path, exist_ok=True)
images_generated_path = 'website/static/images/generated'
os.makedirs(images_generated_path, exist_ok=True)

source_path = 'website/static/sounds/3_sound.mp3'
destination_path = 'website/static/sounds/generated/3_sound.mp3'
shutil.copy(source_path, destination_path)