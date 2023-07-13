import RPi.GPIO as GPIO
import time
import pyaudio
import wave
from pydub import AudioSegment
from wit import Wit
import json
from gtts import gTTS
from io import BytesIO
import numpy as np
from gtts import gTTS
import os
from scipy.io.wavfile import write

GPIO.setwarnings(False)
client = Wit("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, False)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.output(13, False)
GPIO.output(19, False)
GPIO.output(26, False)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, False)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, False)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 512

def speak(message):
  tts = gTTS(message, lang='es-us')
  tts.save('test.mp3')
  os.system("mpg321 'test.mp3'")

while True:
  if not GPIO.input(17):
    GPIO.output(4, True)
    time.sleep(0.1)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
    print("Listening...")
    frames = []
    while not GPIO.input(17):
      data = stream.read(CHUNK)
      frames.append(data)
    for i in range(int(RATE/CHUNK/2)):
      data = stream.read(CHUNK)
      frames.append(data)
    GPIO.output(4, False)
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open("testing.wav", 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    wav_file = AudioSegment.from_file(file="testing.wav", format="wav")
    wav_file_new = wav_file.set_frame_rate(16000)
    new_wav_file = wav_file_new + 20
    file_handle = new_wav_file.export("output.wav", format="wav")

    resp = None
    with open('output.wav', 'rb') as f:
      resp = client.speech(f, {'Content-Type': 'audio/wav'})
    payload = json.dumps(resp)
    topic = json.loads(payload)['intents'][0]['name']
    if topic == "luz_on_off":
      value = json.loads(payload)['traits']['wit$on_off'][0]['value']
      if value=="on":
        GPIO.output(24, True)
        speak('Señor las luces están encendidas.')
      elif value=="off":
        GPIO.output(24, False)
        speak('Señor las luces están apagadas.')
    elif topic == "vent_on_off":
      value = json.loads(payload)['traits']['wit$on_off'][0]['value']
      if value=="on":
        GPIO.output(22, True)
        speak('Señor la ventilación está encendida.')
      elif value=="off":
        GPIO.output(22, False)
        speak('Señor la ventilación está apagada.')
    elif topic == "rgb":
      value = json.loads(payload)['traits']['wit_color'][0]['value']
      if value=="blue":
        GPIO.output(13, True)
        GPIO.output(19, False)
        GPIO.output(26, False)
        speak('Señor el led cambió a color azul.')
      elif value=="red":
        GPIO.output(13, False)
        GPIO.output(19, True)
        GPIO.output(26, False)
        speak('Señor el led cambió a color rojo.')
      elif value=="green":
        GPIO.output(13, False)
        GPIO.output(19, False)
        GPIO.output(26, True)
        speak('Señor el led cambió a color verde.')

  time.sleep(0.1)
