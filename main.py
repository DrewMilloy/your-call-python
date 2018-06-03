#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(description='Record and play 1 minute audio')
parser.add_argument('-k', action='store_true', help='use keyboard instead of GPIO')
parser.add_argument('-d', default=15, help='recording duration (seconds)')
parser.add_argument('-f', action='store_false', help='fake commands - print instead of running aplay/arecord')
args = parser.parse_args()

import platform
import keyboard

run_commands = args.f
force_keyboard = args.k

if platform.machine() == 'x86_64':
    from fakegpio import GPIO
    run_commands = 0
else:
    import RPi.GPIO as GPIO

PLAY_BUTTON = 24
RECORD_BUTTON = 25

GPIO.setmode(GPIO.BCM)     # set up BCM GPIO numbering
GPIO.setup(PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RECORD_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

import os
import random
from datetime import datetime
from time import sleep     # this lets us have a time delay (see line 15)

RECORDING_DURATION = args.d # TODO make this 60 seconds

# depends on the 'usbmount' package
BASE_PATH_FALLBACK = '/home/pi/audio'
USB_PATH_PARENT = '/media/usb'

PATH_RECORDING = 'recordings'
PATH_PLAYBACK = 'moderated'

PATH_LOCAL_DIR = os.path.dirname(os.path.realpath(__file__))

PATH_PROMPT = 'prompt.wav'
PATH_START_BEEP = 'beep1.wav'
PATH_END_BEEP = 'beep2.wav'
PATH_END_PLAYBACK_BEEP = 'beep3.wav'

COMMAND_RECORD = "arecord --device=default:CARD=U0x4b40x306 --format S16_LE --rate 44100 -c1 -d{} {}" # duration + filename
COMMAND_PLAY = "aplay --device=default:CARD=U0x4b40x306 {}" # filename

STATE_WAITING = 0
STATE_PLAYING = 1
STATE_PLAYBACK_ENDED = 2
STATE_PROMPT_FOR_RECORDING = 3
STATE_RECORDING = 4
STATE_RECORDING_ENDED = 5

state = STATE_WAITING

def get_usb_folder():
    usb_paths = os.listdir(USB_PATH_PARENT)
    if len(usb_paths) > 0:
        return USB_PATH_PARENT
    else:
        return BASE_PATH_FALLBACK

def is_play_pressed():
    if force_keyboard:
        return keyboard.is_pressed('p')
    else:
        return GPIO.input(PLAY_BUTTON)

def is_record_pressed():
    if force_keyboard:
        return keyboard.is_pressed('r')
    else:
        return GPIO.input(RECORD_BUTTON)

def get_current_timestamp():
    current_datetime = datetime.utcnow()
    return current_datetime.strftime('%Y%m%d-%H%M%S')

def choose_a_file(folder):
    list_of_files = os.listdir(folder)
    return random.choice (list_of_files) if list_of_files else None

def play_local_audio_file(local_file_to_play):
    absolute_path = os.path.join(PATH_LOCAL_DIR, local_file_to_play)
    play_audio_file(absolute_path)

def play_audio_file(file_to_play):
    play_command = COMMAND_PLAY.format(file_to_play)
    execute_command(play_command)

def record_audio_file(file_to_record):
    record_command = COMMAND_RECORD.format(RECORDING_DURATION, file_to_record)
    execute_command(record_command)

def execute_command(command):
    if run_commands:
        os.system(command)
    else:
        print(command)
        sleep(1)

try:
    while True:
        if state == STATE_WAITING:            # this will carry on until you hit CTRL+C
            if is_play_pressed():
                print ("Starting Playback")
                state = STATE_PLAYING
            elif is_record_pressed():
                print ("Starting Recording")
                state = STATE_PROMPT_FOR_RECORDING
            sleep(0.1)         # wait 0.1 seconds
        elif state == STATE_PLAYING:
            # find a recording
            playback_path = os.path.join(get_usb_folder(), PATH_PLAYBACK)
            chosen_file = choose_a_file(playback_path)
            if chosen_file:
                file_to_play = os.path.join(playback_path, chosen_file)
                # play the recording
                play_audio_file(file_to_play)
            state = STATE_PLAYBACK_ENDED
            # play some kind of tone
            play_local_audio_file(PATH_END_PLAYBACK_BEEP)
            state = STATE_WAITING
        elif state == STATE_PROMPT_FOR_RECORDING:
            # play the record prompt
            play_local_audio_file(PATH_PROMPT)
            play_local_audio_file(PATH_START_BEEP)
            state = STATE_RECORDING
            # record x minutes of audio
            recording_path = os.path.join(get_usb_folder(), PATH_RECORDING)
            file_to_record = os.path.join(recording_path, get_current_timestamp() + ".wav")
            record_audio_file(file_to_record)
            state = STATE_RECORDING_ENDED
            # play end tone
            play_local_audio_file(PATH_END_BEEP)
            state = STATE_WAITING
finally:
    GPIO.cleanup()
