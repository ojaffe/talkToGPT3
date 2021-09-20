import re
import sys

import openai

import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QDesktopWidget, QPlainTextEdit

# initialize Text-to-speech engine

engine = pyttsx3.init()

openai.api_key = ""

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, " \
         "and very friendly." \
         "-:Hello who are you?" \
         "Val:I am an AI created by OpenAI. How can I help you today?" \
         "-:What is your name?" \
         "Val:My name is Val."
initial_prompt = prompt

r = sr.Recognizer()


def formatPrompt(x):
    indicies = [m.start() for m in re.finditer('-:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    indicies = [m.start() for m in re.finditer('Val:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    return x


def recordAudio():
    global prompt

    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        userInput = r.recognize_sphinx(audio)

        if userInput != "exit":
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

            print("Ready to record...")
            return prompt

    except sr.UnknownValueError:
        print("Error: unknown value!")
        exit()


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = "Talk to GPT-3"
        self.left = 10
        self.top = 10
        self.width = 600
        self.height = 480

        self.initUI()
        self.deleteConversationHistory()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

        self.start_button = QPushButton('Start Recording', self)
        self.start_button.resize(160, 30)
        self.start_button.move(20, 20)
        self.start_button.clicked.connect(self.record)

        self.delete_button = QPushButton('Delete conversation history', self)
        self.delete_button.resize(160, 30)
        self.delete_button.move(20, 60)
        self.delete_button.clicked.connect(self.deleteConversationHistory)

        self.stop_button = QPushButton('Exit', self)
        self.stop_button.resize(160, 30)
        self.stop_button.move(20, 100)
        self.stop_button.clicked.connect(app.instance().quit)

        # Create textbox
        self.textbox = QPlainTextEdit(self)
        self.textbox.move(200, 20)
        self.textbox.resize(370, 400)

        self.show()

    def record(self):
        new_prompt = recordAudio()
        self.updateTextbox(new_prompt)

    def deleteConversationHistory(self):
        self.updateTextbox(initial_prompt)

    def updateTextbox(self, text):
        self.textbox.setPlainText(formatPrompt(text))

    def center(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(int((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  int((resolution.height() / 2) - (self.frameSize().height() / 2)))


app = QApplication(sys.argv)
app.setStyle('Fusion')
ex = App()
sys.exit(app.exec_())





