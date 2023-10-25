from gtts import gTTS 
  
# Passing the text and language to the engine,  
# here we have marked slow=False. Which tells  
# the module that the converted audio should  
# have a high speed 
myobj = gTTS(text="hi there", lang='en', slow=False) 
  
# Saving the converted audio in a mp3 file named 
# welcome  
