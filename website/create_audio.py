from gtts import gTTS 


text = "Meet George, George is a 2nd grader struggling with how to pronounce certain words. George wants to know what movies or books series you like so he can learn from you about different letter sounds! Help George learn to read by selecting the characters that correspond to each part of the word. If you can't remember who a certain character represents, ask George; he is sure to know them all."
language = 'en'

welcome = gTTS(text=text, lang=language, slow=False)
welcome.save("welcome.mp3")

text_2 = "What's your all-time favorite movie or book franchise? Think of epic stories like Star Wars, Harry Potter, or Marvel! Share with George!"
franchise = gTTS(text=text_2, lang=language, slow=False)
franchise.save("franchise.mp3")