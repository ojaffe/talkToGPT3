from __future__ import division

import re
import sys
import os
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

from google.cloud import speech, texttospeech
import openai
from pygame import mixer
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QDesktopWidget, QPlainTextEdit, \
    QLineEdit

from mic import MicrophoneStream, listen_print_loop


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

openai.api_key = ""
dir_path = ""

prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly." \
         "Human: Hello, who are you?" \
         "AI: I am an AI created by OpenAI. How can I help you today?"
initial_prompt = prompt


# Given human input and current prompt, feed both as one into API, play response as audio then return response
def callGPT(userInput):
    global prompt
    prompt += "Human:" + userInput
    prompt += "AI:"
    response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150, temperature=0.6,
                                        stop=["Human:"])
    prompt += response.choices[0]["text"]

    # Play response through audio
    synthesize_and_play_text(response.choices[0]["text"])

    return prompt


# Add '\n\n' before each human or AI dialogue
def formatPrompt(x):
    indicies = [m.start() for m in re.finditer('Human:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    indicies = [m.start() for m in re.finditer('AI:', x)]
    for y in reversed(indicies):
        x = x[:y] + '\n\n' + x[y:]
    return x


# Google TTS, then play audio file
def synthesize_and_play_text(text):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-GB",
        name="en-GB-Wavenet-B",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=1,
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    # Load and play outputted audio
    mixer.init()
    mixer.music.load(os.path.join(dir_path, "output.mp3"))
    mixer.music.play()

    # Wait until audio has finished playing, load dummy audio file so os can delete output
    while mixer.music.get_busy():
        pass
    mixer.music.load(os.path.join(dir_path, "dummy.mp3"))
    os.remove(os.path.join(dir_path, "output.mp3"))


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
        language_code = "en-US"

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            text = listen_print_loop(responses)

            new_prompt = callGPT(text)
            self.updateTextbox(new_prompt)

    def typeToGPT3(self):
        self.textbox.setPlainText("")
        new_prompt = callGPT(self.typeTextbox.text())
        self.updateTextbox(new_prompt)

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
