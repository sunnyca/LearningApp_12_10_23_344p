from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from flask import session
from .models import Note
from .models import Franchise
from . import db
import json
from flask import Flask, g

import openai
import urllib.request
from PIL import Image
import matplotlib.pyplot as plt

import urllib.request
import ssl
import requests
import os 

#IMPORTANT OR ELSE WE CANNOT MAKE THIS WORK 
ssl._create_default_https_context = ssl._create_unverified_context



views = Blueprint('views', __name__)
openai.api_key = "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"


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
    return render_template("intro_flow_1.html", user=current_user)

@views.route('/intro_flow_2', methods=['GET', 'POST'])
@login_required
def intro_flow_2():
    if request.method == 'POST':
        f = request.form.get('franchise-input')

        # Create a new UserResponse instance and save it to the database
        user_response = Franchise(franchise=f)
        db.session.add(user_response)
        db.session.commit()

        return redirect(url_for('views.intro_flow_3')) 
    return render_template('intro_flow_2.html', user=current_user)

@views.route('/intro_flow_3', methods=['GET'])
@login_required
def intro_flow_3():
    # Your existing code to retrieve the franchise data
    franchise = Franchise.query.first()

    # Add the generative AI component
    yourStory = "Star Wars"  # Hard Coded Currently (Needs to be dynamic)

    botResponse = openai.Completion.create(
        model="text-davinci-003",
        prompt="Print out a picture that describes this: " + yourStory,
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
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    image_response = requests.get(image_url)
    #if image_response.status_code == 200:
    #    with open("static/result.png", "wb") as image_file:
    #        image_file.write(image_response.content)

    # Now, you can pass the image URL to the HTML template
    #image_url = url_for('static', filename='result.png')

    # add below , image_url=image_url
    return render_template('intro_flow_3.html', user=current_user, franchise=franchise)

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
