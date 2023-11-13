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

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

import urllib.request
import ssl
import requests
import os 
import io
import warnings

from gtts import gTTS 

order = ["sh","p","b","i"] #this needs to be updated as we introduce more letters 
characters = []
image_info = {'franchise_sh.png':' it says /sh/',
                'franchise_p.png':" it says /p/",
                'franchise_b.png':' it says /b/',
                'franchise_i.png':' it says /i/',
                'franchise_logo.png':''}

#IMPORTANT OR ELSE WE CANNOT MAKE THIS WORK 
ssl._create_default_https_context = ssl._create_unverified_context

views = Blueprint('views', __name__)

os.environ['GPT_KEY'] = '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'
 # openai.api_key = os.environ['API_KEY'] : this doesn't work on my computer, but it should work on yours

os.environ['STABILITY_KEY'] = 'sk-rr1JnmVdLgOHz6IHaKx5wXAUza49ZnRvKcghatvAbumFO6DZ' #this should be done locally 
openai.api_key = os.environ['GPT_KEY']

api_key = os.environ['STABILITY_KEY']
stability_api = client.StabilityInference(
    key=api_key, # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-xl-1024-v1-0", # Set the engine to use for generation.
    # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
)




#generates 4 images for a given sound in a given franchise
def generate_images(sound, prompt=0):
        botResponse = openai.Completion.create(
            model="text-davinci-003",
            prompt= "give me a person from" + current_user.franchise + "that starts with the" + sound + "sound. Only responded with that person's or objects name.",
            temperature=0.5,
            max_tokens=120,
            top_p=1.0,
            frequency_penalty=0.8,
            presence_penalty=0.0,
        )
        botResponse = botResponse["choices"][0]["text"].strip()
        

        answers = stability_api.generate(
            prompt=botResponse,
            steps=50, 
            cfg_scale=8.0, 
            width=1024, # Generation width, defaults to 512 if not included.
            height=1024, # Generation height, defaults to 512 if not included.
            samples=4, # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M # Set the sampling algorithm. Defaults to SAMPLER_K_DPP_2M if not included.
        ) 
        i = 0
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                            img = Image.open(io.BytesIO(artifact.binary))
                img.save("website/static/franchise_"+sound+str(i)+".png")
            i += 1
        
        if prompt == 1: #lets us return the prompt for testing purposes
            return botResponse





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

@views.route('/intro_audio_1', methods=['GET', 'POST'])
@login_required
def intro_audio_1():
    os.system("website/static/0.mp3")
    return render_template("intro_flow_1.html", user=current_user)
    

@views.route('/intro_flow_2', methods=['GET', 'POST'])
@login_required
def intro_flow_2():
    current_user_id = current_user.id
    if current_user.franchise != None:
        return redirect(url_for('views.intro_flow_3'))
    elif request.method == 'POST':
        print(request.form)

        franchise = request.form.get('franchise')        

        # Query the User model to find the user by ID
        user = User.query.filter_by(id=current_user_id).first()
        user.franchise = franchise
        db.session.commit()

        return redirect(url_for('views.intro_flow_3'))
    else: 
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

    if not os.path.exists("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/franchise_logo.png"): #Checks to see if image already exists, if it exists does not regenerate 

        print(yourStory)

        answers = stability_api.generate(
            prompt="A visual cartoon version of the " + yourStory + " franchise",
            steps=50, 
            cfg_scale=8.0, 
            width=512, # Generation width, defaults to 512 if not included.
            height=512, # Generation height, defaults to 512 if not included.
            samples=1, # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M # Set the sampling algorithm. Defaults to SAMPLER_K_DPP_2M if not included.
        ) 
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                            img = Image.open(io.BytesIO(artifact.binary))
                img.save("website/static/franchise_logo.png")


        return render_template('intro_flow_3.html', user=current_user, franchise=franchise)
    else:
        return render_template('intro_flow_3.html', user=current_user, franchise=franchise)

@views.route('/intro_flow_4', methods=['GET', 'POST'])
@login_required
def intro_flow_4():
    #Checks to see if image already exists, if it exists does not regenerate 
    if not os.path.exists("website/static/franchise_sh1.png"): 
        character = generate_images("sh",1)
        characters.append(character)
        return render_template("intro_flow_4.html", user=current_user,character=character)
    else:
        botResponse = openai.Completion.create(
            model="text-davinci-003",
            prompt= "give me a person from" + current_user.franchise + "that starts with the sh sound. Only responded with that person's or objects name.",
            temperature=0.5,
            max_tokens=120,
            top_p=1.0,
            frequency_penalty=0.8,
            presence_penalty=0.0,
        )
        character = botResponse["choices"][0]["text"].strip() 
        return render_template("intro_flow_4.html", user=current_user,character=character)



@views.route('/regenerate', methods=['GET', 'POST'])
@login_required
def regenerate():
    if request.form.get('sound') in order:
        index = order.index(request.form.get('sound'))
        i = str(index + 4)
    if request.method == 'POST':
        print(request.form.get('sound'))
        character= generate_images(request.form.get('sound'),1)
        characters[i] = (character)
        return render_template("intro_flow_"+ i +".html", user=current_user, character=character) 
    else:
        return render_template("intro_flow_"+ i +".html", user=current_user)


 #There should be a way to do whats below in one function, but I am to tired to figure it out at the moment. 

@views.route('/store_image_1', methods=['GET', 'POST'])
@login_required
def store_image_1():
    if request.method == 'POST':
        selected_image = int(request.form['selected_image'])
        for i in range(0,4):
            if i != selected_image:
                os.remove("website/static/franchise_sh"+str(i)+".png")
            else:
                os.rename("website/static/franchise_sh"+str(i)+".png", "website/static/franchise_sh.png")
        character = generate_images('p',1)
        characters.append(character)
        return render_template("intro_flow_5.html", user=current_user,character=character)
    else:
        return render_template("intro_flow_4.html", user=current_user)
    

@views.route('/store_image_2', methods=['GET', 'POST'])
@login_required
def store_image_2():
    if request.method == 'POST':
        selected_image = int(request.form['selected_image'])
        for i in range(0,4):
            if i-1 != selected_image:
                os.remove("website/static/franchise_p"+str(i)+".png")
            else:
                os.rename("website/static/franchise_p"+str(i)+".png", "website/static/franchise_p.png") #renames the selected image to franchise_p.png
        character = generate_images('b',1)
        characters.append(character)
        return render_template("intro_flow_6.html", user=current_user,character=character)
    else:
        return render_template("intro_flow_5.html", user=current_user)
    
@views.route('/store_image_3', methods=['GET', 'POST'])
@login_required
def store_image_3():
    if request.method == 'POST':
        selected_image = int(request.form['selected_image'])
        for i in range(0,4):
            if i != selected_image:
                os.remove("website/static/franchise_b"+str(i)+".png")
            else:
                os.rename("website/static/franchise_b"+str(i)+".png", "website/static/franchise_b.png")
        character = generate_images('i',1)
        characters.append(character)
        return render_template("intro_flow_7.html", user=current_user,character=character)
    else:
        return render_template("intro_flow_6.html", user=current_user)
    
@views.route('/store_image_i', methods=['GET', 'POST'])
@login_required
def store_image_i():
    if request.method == 'POST':
        selected_image = int(request.form['selected_image'])
        for i in range(0,4):
            if i != selected_image:
                os.remove("website/static/franchise_i"+str(i)+".png")
            else:
                os.rename("website/static/franchise_i"+str(i)+".png", "website/static/franchise_i.png")
        return progress_tracker()
    else:
        return render_template("intro_flow_6.html", user=current_user)

#Again above functions should probably be one function.




@views.route('/games', methods=['GET', 'POST'])
@login_required
def games():
    return render_template("games.html", user=current_user)



#this is broken because the characters list is not globaly defined I believe, so the first time you itterate through 
#it works but the second time characters is an empty list so breaks. We probably have to add characters to database 
#but I didn't know how to do that.
@views.route('/progress_tracker', methods=['GET', 'POST'])
@login_required
def progress_tracker():
    characters.append('your franchise logo!')
    print(characters)
    existing_images = [image for image in image_info if os.path.exists(f"website/static/{image}")]
    for image in existing_images:
        image_info[image] = 'This is ' + characters[existing_images.index(image)] + image_info[image]
    return render_template("progress_tracker.html", user=current_user,existing_images=existing_images,image_info=image_info)
    
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
