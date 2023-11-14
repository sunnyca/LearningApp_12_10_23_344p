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
from openai import OpenAI



import urllib.request
from PIL import Image
import matplotlib.pyplot as plt
from playsound import playsound

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
# this keeps track of the characters that have been generated so far, could probably go into the database 
# for the user but doing it locally now 
characters = {'sh':'',
              'p':'',
              'b':'',
              'i':'',
              'logo':" "}

#IMPORTANT OR ELSE WE CANNOT MAKE THIS WORK 
ssl._create_default_https_context = ssl._create_unverified_context

views = Blueprint('views', __name__)

#os.environ['GPT_KEY'] = 
client_1 = OpenAI(api_key=os.environ['GPT_KEY'])
# openai.api_key = os.environ['API_KEY'] : this doesn't work on my computer, but it should work on yours

# os.environ['STABILITY_KEY'] = '' #this should be done locally 

#initialize the stability api
api_key = os.environ['STABILITY_KEY']
stability_api = client.StabilityInference(
    key=api_key, # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-xl-1024-v1-0", # Set the engine to use for generation.
    # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
)




#generates 4 images for a given sound in a given franchise
def generate_images(sound, prompt=0):
        #calls gpt model to get character 
        botResponse = client_1.completions.create(model="text-davinci-003",
        prompt= "give me a person from" + current_user.franchise + "that starts with the" + sound + "sound. Only responded with that person's or objects name.",
        temperature=0.5,
        max_tokens=120,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.0)
        botResponse = botResponse.choices[0].text.lstrip()
        
        #uses stability to generate images
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
        # names and stores images - again done locally, if we want to publish this would neeed to be pushed to some cloud server 
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






#starts intro 
@views.route('/intro_flow_1', methods=['GET', 'POST'])
@login_required
def intro_flow_1():
    return render_template("intro_flow_1.html", user=current_user)

#plays audio for first clip 
#audio plays continously once clicked, even when continueing through app 
@views.route('/intro_audio_1', methods=['POST'])
@login_required
def intro_audio_1():
    playsound("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/0.mp3")
    return render_template("intro_flow_1.html", user=current_user)

#plays second audio clip, same caveat 
@views.route('/audio_2', methods=['POST'])
@login_required
def audio_2():
    playsound("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/1.mp3")
    return render_template("intro_flow_2.html", user=current_user)

#plays third audio clip, same caveat
# this one is slower cause we need to generate including franchise name, so can't do when site is first loaded 
@views.route('/audio_3', methods=['POST'])
@login_required
def audio_3():
    #checks to see if file has been generated 
    #could probably 
    if not os.path.exists("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/3.mp3"):
        #uses openai to generate audio
        client_2 = OpenAI()
        user = User.query.filter_by(id=current_user.id).first()
        response1 = client_2.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="You're ready to start learning with George! He is so excited to learn more about" +user.franchise+"! The next screen will help teach you letters using characters from " + user.franchise + "."
        )
        #saves audio 
        response1.stream_to_file("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/3.mp3")
    #plays audio 
    playsound("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/3.mp3")
    return render_template("intro_flow_3.html", user=current_user)

#second screen of intro flow, asks for franchise name
@views.route('/intro_flow_2', methods=['GET', 'POST'])
@login_required
def intro_flow_2():
    current_user_id = current_user.id
    #skips this screen if user already has a franchise 
    if current_user.franchise != None:
        return redirect(url_for('views.intro_flow_3'))
    #else asks for franchise name and stores it in database
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

#third screen of intro flow, generates logo
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

    #Checks to see if image already exists, if it exists does not regenerate 
    if not os.path.exists("/Users/keeganharkavy/Desktop/Code/LearningApp/website/static/franchise_logo.png"):
        #included for testing 
        print(yourStory)
        #generates logo
        answers = stability_api.generate(
            prompt="A visual cartoon version of the " + yourStory + " franchise",
            steps=50, 
            cfg_scale=8.0, 
            width=512, # Generation width, defaults to 512 if not included.
            height=512, # Generation height, defaults to 512 if not included.
            samples=1, # Number of images to generate, defaults to 1 if not included.
            sampler=generation.SAMPLER_K_DPMPP_2M # Set the sampling algorithm. Defaults to SAMPLER_K_DPP_2M if not included.
        ) 
        #saves logo
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

#fourth screen of intro flow, generates images for sh sound 
@views.route('/intro_flow_4', methods=['GET', 'POST'])
@login_required
def intro_flow_4():
    #Checks to see if image already exists, if it exists skips to next sound 
    if not os.path.exists("website/static/franchise_sh.png"): 
        character = generate_images("sh",1)
        characters['sh']= character
        return render_template("intro_flow_4.html", user=current_user,character=character)
    else:
        return store_image_1()


#if all four options are bad this should generate 4 new images, changed a bunch recently so not sure
#this is still working
@views.route('/regenerate', methods=['GET', 'POST'])
@login_required
def regenerate():
    if request.form.get('sound') in order:
        index = order.index(request.form.get('sound'))
        #include so we can index to current template
        i = str(index + 4)
    if request.method == 'POST':
        print(request.form.get('sound'))
        character= generate_images(request.form.get('sound'),1)
        characters[request.form.get('sound')] = (character)
        return render_template("intro_flow_"+ i +".html", user=current_user, character=character) 
    else:
        return render_template("intro_flow_"+ i +".html", user=current_user)


 #There should be a way to do whats below in one function, but I am to tired to figure it out at the moment. 

#stores image for sh sound
@views.route('/store_image_1', methods=['GET', 'POST'])
@login_required
def store_image_1():
    #checks to see if this is from button or redirect
    if request.method == 'POST':
        #if from button removes all but selected image and then renames selected image to franchise_sh.png
        selected_image = int(request.form['selected_image'])
        for i in range(0,4):
            if i != selected_image:
                os.remove("website/static/franchise_sh"+str(i)+".png")
            else:
                os.rename("website/static/franchise_sh"+str(i)+".png", "website/static/franchise_sh.png")
    #checks to see if next sound exists already, if not generates images for next sound
    if not os.path.exists("website/static/franchise_p.png"):
        character = generate_images('p',1)
        characters["p"] = (character)
        return render_template("intro_flow_5.html", user=current_user,character=character)
    #if next sound exists skips to next sound
    else:
        return store_image_2()
    
#stores image for p sound (same code so not commented)
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
    if not os.path.exists("website/static/franchise_b.png"): 
        character = generate_images('b',1)
        characters['b']=(character)
        return render_template("intro_flow_6.html", user=current_user,character=character)
    else: 
        return store_image_3()

#stores image for b sound (same code so not commented)    
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
    if not os.path.exists("website/static/franchise_i.png"): 
        character = generate_images('i',1)
        characters['i']=(character)
        return render_template("intro_flow_7.html", user=current_user,character=character)
    else:
        return store_image_i()

#stores image for i sound (same code so not commented) 
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
        return progress_tracker()

#Again above functions should probably be one function.




@views.route('/games', methods=['GET', 'POST'])
@login_required
def games():
    return render_template("games.html", user=current_user)



#this is the page that will be used to check progress on flashcards 
@views.route('/progress_tracker', methods=['GET', 'POST'])
@login_required
def progress_tracker():
    #created so we can find each image and its corresponding character
    image_info = {'sh':' they says /sh/',
                'p':" they says /p/",
                'b':' they says /b/',
                'i':' they says /i/',
                'logo':'your franchise logo!'}
    print(characters)
    #This is confusedly named but it itterates through image_info and then returns the keys (honestly not sure why I did this but it is here)
    existing_images = [image for image in image_info if os.path.exists(f"website/static/franchise_{image}.png")]
    #loops through each key and updates image_info to say what we want to display
    for image in existing_images:
        image_info[image] = 'This is ' + characters[image] + image_info[image]
    #returns enough information to display the images and their corresponding characters
    return render_template("progress_tracker.html", user=current_user,existing_images=existing_images,image_info=image_info)


#legacy code from template 
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

#more legacy code 
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
