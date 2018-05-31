
# import RPi.GPIO as GPIO 
# GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering  
# GPIO.setup(PLAY_BUTTON, GPIO.IN)
# GPIO.setup(RECORD_BUTTON, GPIO.IN)

import keyboard 
import os
import random
from datetime import datetime
from time import sleep     # this lets us have a time delay (see line 15)  
PLAY_BUTTON = 24
RECORD_BUTTON = 25

RECORDING_DURATION = 15 # TODO make this 60 seconds

PATH_RECORDING = '/opt/pi/recordings' # TODO make this the USB stick
PATH_PLAYBACK = '/opt/pi/moderated' # TODO make this the USB stick

PATH_START_BEEP = './beep1.wav'
PATH_END_BEEP = './beep2.wav'
PATH_END_PLAYBACK_BEEP = './beep3.wav'

COMMAND_RECORD = "arecord --device=hw:1,0 --format S16_LE --rate 44100 -c1 -d{} {}" # duration + filename
COMMAND_PLAY = "aplay {}" # filename

STATE_WAITING = 0
STATE_PLAYING = 1
STATE_PLAYBACK_ENDED = 2
STATE_PROMPT_FOR_RECORDING = 3
STATE_RECORDING = 4
STATE_RECORDING_ENDED = 5

state = STATE_WAITING

def is_play_pressed():
    # return GPIO.input(PLAY_BUTTON)
    return keyboard.is_pressed('p')
    
def is_record_pressed():
    # return GPIO.input(RECORD_BUTTON)
    return keyboard.is_pressed('r')

def get_current_timestamp():
    current_datetime = datetime.utcnow()
    return current_datetime.strftime('%Y%m%d-%H%M%S')

def choose_a_file():
    list_of_files = os.listdir(PATH_PLAYBACK)
    return random.choice (list_of_files)

def play_audio_file(file_to_play):
    play_command = COMMAND_PLAY.format(file_to_play)
    print(play_command)

def record_audio_file(file_to_record):
    record_command = COMMAND_RECORD.format(RECORDING_DURATION, file_to_record)
    print(record_command)

try:
    while True:
        while state == STATE_WAITING:            # this will carry on until you hit CTRL+C  
            if is_play_pressed(): 
                print ("Starting Playback")  
                state = STATE_PLAYING
            elif is_record_pressed():
                print ("Starting Recording")
                state = STATE_PROMPT_FOR_RECORDING
            sleep(0.1)         # wait 0.1 seconds  
        if state == STATE_PLAYING:
            # find a recording
            file_to_play = os.path.join(PATH_PLAYBACK, choose_a_file())
            # play the recording
            play_audio_file(file_to_play)
            state = STATE_PLAYBACK_ENDED
            # play some kind of tone
            play_audio_file(PATH_END_PLAYBACK_BEEP)
            sleep(1)
            state = STATE_WAITING
        elif state == STATE_PROMPT_FOR_RECORDING:
            # play the record prompt
            play_audio_file(PATH_START_BEEP)
            state = STATE_RECORDING
            # record x minutes of audio
            file_to_record = os.path.join(PATH_RECORDING, get_current_timestamp() + ".wav")
            record_audio_file(file_to_record)
            state = STATE_RECORDING_ENDED
            # play end tone
            play_audio_file(PATH_END_BEEP)
            sleep(1)
            state = STATE_WAITING
finally: 
    GPIO.cleanup()