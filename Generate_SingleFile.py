# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 12:00:38 2021

@author: olehe

This should generate audio for Sander's experiment
Only one repeat, and at given BPM.

Usage: Generate_SingleFile.py tempo1 tempo2 tempo3 tempoN
Example for generating at 80, 120, 140, and 150:
	Generate_SingleFile.py 80 120 140 150


Requirements:
Python 3.8
fluidsynth needs to be installed, tested with 2.2.2 on Windows 10
fluidsynth needs a soundfont called default.sf2
Most packages in requirements.txt


"""

#%% Imports

import mido
import os
import glob
#import math
#from scipy.io import wavfile
import subprocess
import time
#import random
#import numpy as np
#import pandas as pd
import sys




#%% Functions

def get_tempo(mid):
	for track in mid.tracks:
		for msg in track:
			if msg.type == 'set_tempo':
				return msg.tempo
			else:
				return 0


def change_tempo(mid, tempo):
	# strip existing set_tempo messages and replace
	# for some reason, I believe the tempo needs to be doubled,
	# probably because the way the midi files are written.
	tempo = tempo * 2
	
	output = mido.MidiFile(type=1)
	tempoTicks = mido.bpm2tempo(tempo)
	
	for thisTrack in mid.tracks:
		track = mido.MidiTrack()
		for msg in thisTrack:	
			if msg.type == 'set_tempo':
				track.append(mido.MetaMessage('set_tempo', tempo=tempoTicks))
			else:
				track.append(msg)
		output.tracks.append(track)
	
	#output.tracks.append(track)
	#output.tracks.append(mid.tracks[1])
	return output



def write_wav(midiName, name):
	#REPLACE THIS WITH YOUR OWN FLUIDSYNTH
	fluidsynth = 'C:/Users/olehe/Documents/GitHub/SanderGenerator/fluidsynth-2.2.2/bin/fluidsynth.exe'
	result = subprocess.run([fluidsynth, "-i", "-q", "default.sf2", midiName, "-T", "wav", "-F", name], shell=True)
	# This doesn't always play nice, but it's solved by simply letting it sleep a bit.
	# I've not tested without the sleep, so it could possible work without it.
	time.sleep(1)
	
	return
			

#%% General variables and experiment setup

# Input arguments

nArgs = len(sys.argv)

# Check args, or revert to default
if nArgs > 2:
	tempoList = [int(i) for i in list(sys.argv[1:])]
else:
	tempoList = 120

if max(tempoList) > 240 or min(tempoList) < 60:
	print('UNUSUAL TEMPO DETECTED! Are you sure about this?')

print('Generating stimuli at', str(tempoList), 'BPM.')


# create folders

if not os.path.isdir('stims'):
	os.mkdir('stims')

for tempo in tempoList:
	thisPath = os.path.join('stims', str(tempo))
	if not os.path.isdir(thisPath):
		os.mkdir(thisPath)



# levels of our stimuli, in order.
listLevels = ['HR1HH3',
			'HR1MH2',
			'HR3HH5',
			'HR3MH4',
			'LR3HH3',
			'LR3MH2',
			'LR7HH3',
			'LR7MH4',
			'MariatoClaveMR5HH3',
			'MariatoClaveMR5MH2',
			'SonClaveMR1HH5',
			'SonClaveMR1MH4',
			'Metro1MH',
			'Metro1HH',
			'Metro2MH',
			'Metro2HH',
			'practiceMetroLH2',
			'practiceHR1LH3',
			'practiceRumbaClaveMR2LH2',
			'practiceLR6LH2']



#%% Cleaning

# delete all files in scratchFolders, so they don't sneak in.


scratchMidiFiles = glob.glob('scratchMIDI/*.mid')
for f in scratchMidiFiles:
	os.remove(f)	

# this may not remove all files
	
	

#%% Read midi, make wav
# there should be 16 files.

# Hardcoded stimuli MIDI
HR1HH3 = mido.MidiFile('stimMidi/HR1HH3.mid') #
HR1MH2 = mido.MidiFile('stimMidi/HR1MH2.mid') #
HR3HH5 = mido.MidiFile('stimMidi/HR3HH5.mid') #
HR3MH4 = mido.MidiFile('stimMidi/HR3MH4.mid') #
LR3HH3 = mido.MidiFile('stimMidi/LR3HH3.mid') #
LR3MH2 = mido.MidiFile('stimMidi/LR3MH2.mid') #
LR7HH3 = mido.MidiFile('stimMidi/LR7HH3.mid') #
LR7MH4 = mido.MidiFile('stimMidi/LR7MH4.mid') #
MariatoClaveMR5HH3 = mido.MidiFile('stimMidi/MariatoClaveMR5HH3.mid') #
MariatoClaveMR5MH2 = mido.MidiFile('stimMidi/MariatoClaveMR5MH2.mid') #
SonClaveMR1HH5 = mido.MidiFile('stimMidi/SonClaveMR1HH5.mid') #
SonClaveMR1MH4 = mido.MidiFile('stimMidi/SonClaveMR1MH4.mid') #
Metro1MH = mido.MidiFile('stimMidi/Metro1MH.mid')
Metro1HH = mido.MidiFile('stimMidi/Metro1HH.mid')
Metro2MH = mido.MidiFile('stimMidi/Metro2MH.mid')
Metro2HH = mido.MidiFile('stimMidi/Metro2HH.mid')
# the following were added November 16, 2021
practiceMetroLH2 = mido.MidiFile('stimMidi/MetroLH2.mid')
practiceHR1LH3 = mido.MidiFile('stimMidi/HR1LH3.mid')
practiceRumbaClaveMR2LH2 = mido.MidiFile('stimMidi/RumbaClaveMR2LH2.mid')
practiceLR6LH2 = mido.MidiFile('stimMidi/LR6LH2.mid')


allMidi = [HR1HH3,
			HR1MH2,
			HR3HH5,
			HR3MH4,
			LR3HH3,
			LR3MH2,
			LR7HH3,
			LR7MH4,
			MariatoClaveMR5HH3,
			MariatoClaveMR5MH2,
			SonClaveMR1HH5,
			SonClaveMR1MH4,
			Metro1MH,
			Metro1HH,
			Metro2MH,
			Metro2HH,
			practiceMetroLH2,
			practiceHR1LH3,
			practiceRumbaClaveMR2LH2,
			practiceLR6LH2]

# run through, change tempo, make .wav-file
for tempo in tempoList:
	print('Generating stims for', str(tempo), 'BPM.')
	for n, thisStim in enumerate(allMidi):
		tempoChanged = change_tempo(thisStim, tempo)
		saveNameMidi = 'scratchMIDI/' + str(tempo) + '_' + listLevels[n] + '.mid'
		tempoChanged.save(saveNameMidi)
		saveNameWav = 'stims/' + str(tempo) + '/' + listLevels[n] + '.wav'
		write_wav(saveNameMidi, saveNameWav)

print('Done.')


