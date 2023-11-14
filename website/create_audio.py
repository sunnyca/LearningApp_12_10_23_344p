from pathlib import Path
from openai import OpenAI
import openai
import os
from flask import Blueprint, render_template, request, flash, redirect, url_for

create_audio = Blueprint('create_audio', __name__)

texts = ["Meet George, George is a 2nd grader struggling with how to pronounce certain words. George wants to know what movies or books series you like so he can learn from you about different letter sounds! Help George learn to read by selecting the characters that correspond to each part of the word. If you can't remember who a certain character represents, ask George; he is sure to know them all.",
        "What's your all-time favorite movie or book franchise? Think of epic stories like Star Wars, Harry Potter, or Marvel! Share with George!",
        "Goerge learns best by matching sounds to letters. So far he has learned four sounds /i/, /b/, /sh/, and /p/. Lets create some flash cards for each of these sounds! Below are some images generated by George, pick the one that best matches the sound displayed. If none of them are good, click regenerate to get a new set of images. Once you have clicked on an image, the flash card will be created. You can check out all created flashcards in the Progress Tracker tab."        
        ]
os.environ['OPENAI_API_KEY'] = ''


client = OpenAI()
i = 0
for text in texts:
    if not os.path.exists("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/"+ str(i) + ".mp3"):
        response1 = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
        )
        response1.stream_to_file("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/"+ str(i) + ".mp3")
    i += 1

