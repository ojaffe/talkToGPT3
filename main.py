import openai

import pyttsx3
import speech_recognition as sr

# initialize Text-to-speech engine
engine = pyttsx3.init()

openai.api_key = ""

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, " \
         "and very friendly." \
         "-:Hello who are you?" \
         "Val:I am an AI created by OpenAI. How can I help you today?" \
         "-:How do I delete a file on windows?" \
         "Val:Locate the file that you want to delete. Right-click the file, then click Delete on the shortcut menu." \
         "-:How do I sum a list in python?" \
         "Val:sum()" \
         "-:How do I declare a float in C?" \
         "Val:float x;" \
         "-:Write a function in python that sums a list." \
         "Val: def sumList(list):" \
         "return sum(list)"

injectStartText = "Val:"

while True:

    # userInput = input("-:")
    # Get audio input
    userInput = ""
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)

        try:
            userInput = r.recognize_sphinx(audio)
            break
        except sr.UnknownValueError:
            continue

    if userInput == "exit":
        break

    print("-:" + userInput)
    prompt += "-:" + userInput
    prompt += "Val:"
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150, temperature=0,
                                        stop=["-:"])
    prompt += response.choices[0]["text"]
    print("Val:" + response.choices[0]["text"])

    # Play the response
    engine.say(response.choices[0]["text"])
    engine.runAndWait()
