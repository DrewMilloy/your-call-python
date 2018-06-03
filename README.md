# your-call-python

Raspberry Pi-based audio snippet recording and playback system

## Setting up the platform

Starting from a fresh Raspbian Stretch installation:

```
# install required packages
sudo apt-get update
sudo apt-get install git python3-pip alsa-tools
```

Then clone this repo, then set up python dependencies:

```
cd your-call-python
# install python dependencies
pip3 install -r pip_versions.txt
```

## Setting up auto-mount of USB drives



## Running this program

```
usage: main.py [-h] [-k] [-d D] [-f]

Record and play 1 minute audio

optional arguments:
  -h, --help  show this help message and exit
  -k          use keyboard instead of GPIO
  -d D        recording duration (seconds)
  -f          fake commands - print instead of running aplay/arecord
```
