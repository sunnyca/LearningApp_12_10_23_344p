from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from flask import session
from .models import Note
from .models import User
from . import db
import json
from flask import Flask, g
from flask import redirect
from flask import url_for
import openai
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt

import urllib.request
import ssl
import requests
import os 

from gtts import gTTS 
  
  
#IMPORTANT OR ELSE WE CANNOT MAKE THIS WORK 
ssl._create_default_https_context = ssl._create_unverified_context

views = Blueprint('views', __name__)
openai.api_key = os.environ['API_KEY']


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/intro_flow_1', methods=['GET', 'POST'])
@login_required
def intro_flow_1():
    if request.method == 'POST':
        if int(request.form['play']) == 1:
            os.system("mpg321 welcome.mp3")
        else:    
            return render_template("intro_flow_1.html", user=current_user)
    return render_template("intro_flow_1.html", user=current_user)
    

@views.route('/intro_flow_2', methods=['GET', 'POST'])
@login_required
def intro_flow_2():
    if request.method == 'POST':
        print(request.form)

        franchise = request.form.get('franchise')

        current_user_id = current_user.id

        # Query the User model to find the user by ID
        user = User.query.filter_by(id=current_user_id).first()
        user.franchise=franchise
        db.session.commit()

        return redirect(url_for('views.intro_flow_3')) 
    return render_template('intro_flow_2.html', user=current_user)

@views.route('/intro_flow_3', methods=['GET'])
@login_required
def intro_flow_3():
    current_user_id = current_user.id

    # Query the User model to find the user by ID
    user = User.query.filter_by(id=current_user_id).first()

    # Your existing code to retrieve the franchise data
    franchise = user.franchise

    # Add the generative AI component
    yourStory = franchise  # Hard Coded Currently (Needs to be dynamic)

    botResponse = openai.Completion.create(
        model="text-davinci-003",
        prompt="A visual cartoon version of the " + yourStory + " franchise",
        temperature=0.5,
        max_tokens=120,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.0,
    )
    botResponse = botResponse["choices"][0]["text"].strip()

    response = openai.Image.create(
        prompt=botResponse,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    script_path = os.path.abspath(__file__)
    print(f"The path to this script is: {script_path}")

    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        with open("website/static/franchise_logo.png", "wb") as image_file:
            image_file.write(image_response.content)

    image_url = url_for('static', filename='franchise_logo.png')

    return render_template('intro_flow_3.html', user=current_user, franchise=franchise, image_url=image_url)

@views.route('/progress_tracker', methods=['GET', 'POST'])
@login_required
def progress_tracker():

    return render_template("progress_tracker.html", user=current_user)
    
@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
