import os
from openai import OpenAI

os.environ['GPT_KEY'] = ''
client_1 = OpenAI(api_key=os.environ['GPT_KEY'])


botResponse = client_1.completions.create(model="text-davinci-003",
    prompt= "give me a person from star wars that starts with the sound b. Only responded with that person's or objects name.",
    temperature=0.5,
    max_tokens=120, 
    top_p=1.0,
    frequency_penalty=0.8,
    presence_penalty=0.0)
print()
