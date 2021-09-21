import re
import sys

import openai

import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QDesktopWidget, QPlainTextEdit, \
    QLineEdit

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


# Add '\n\n' before each human or AI dialogue
def formatPrompt(x):
    indicies = [m.start() for m in re.finditer('-:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    indicies = [m.start() for m in re.finditer('Val:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    return x


# Open mic, then decode input voice into text
def recordAudio():

    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    try:
        userInput = r.recognize_sphinx(audio)
        return callGPT(userInput)

    except sr.UnknownValueError:
        print("Error: unknown value!")
        exit()


# Given human input and current prompt, feed both as one into API, play response as audio then return response
def callGPT(userInput):
    global prompt
    prompt += "-:" + userInput
    prompt += "Val:"
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150, temperature=0,
                                        stop=["-:"])
    prompt += response.choices[0]["text"]

    # Play the response
    engine.say(response.choices[0]["text"])
    engine.r
    return prompt


# Interface to control functionality and view conversation history
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
        self.stop_button.move(20, 390)
        self.stop_button.clicked.connect(app.instance().quit)

        # Create textbox
        self.textbox = QPlainTextEdit(self)
        self.textbox.resize(370, 400)
        self.textbox.move(200, 20)

        # Type to GPT-3
        self.text_button = QPushButton('Type to GPT-3', self)
        self.text_button.resize(160, 30)
        self.text_button.move(20, 180)
        self.text_button.clicked.connect(self.typeToGPT3)

        self.typeTextbox = QLineEdit(self)
        self.typeTextbox.resize(160, 30)
        self.typeTextbox.move(20, 150)

        self.show()

    def record(self):
        self.start_button.setText("recording...")
        new_prompt = recordAudio()
        self.updateTextbox(new_prompt)
        self.start_button.setText("Start Recording")

    def typeToGPT3(self):
        new_prompt = callGPT(self.typeTextbox.text())
        self.updateTextbox(new_prompt)

    def typePopupClicked(self, i):
        if i.text() == "Apply":
            print("a")

    def deleteConversationHistory(self):
        self.updateTextbox(initial_prompt)
        global prompt
        prompt = initial_prompt

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
