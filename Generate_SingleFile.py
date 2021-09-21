# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 12:00:38 2021

@author: olehe

This should generate audio for Sander's experiment
Only one repeat, and at given BPM.

5- 'LR3 MH2'

7- 'LR3 HH3'

24- 'LR7 MH4'

26- 'LR7 HH5'

33- 'Son Clave MR1 MH4'

35- 'Son Clave MR1 HH5'

50- 'Mariato Clave MR5 MH2'

52- 'Mariato Clave MR5 HH3'

59- 'HR1 MH2'

61- 'HR1 HH3'

69- 'HR3 MH4'

71- 'HR3 HH5'

95- 'METRONOME 2 MH'

94- 'METRONOME 1 MH'

98- 'METRONOME 2 HH'

97- 'METRONOME 1 HH'


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
import math
from scipy.io import wavfile
import subprocess
import time
import random
import numpy as np
import pandas as pd
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
	thisTempo = int(float(sys.argv[1]))
	thisParticipant = sys.argv[2]
else:
	thisTempo = 120
	thisParticipant = 'TestParticipant'

if thisTempo > 240 or thisTempo < 60:
	print('UNUSUAL TEMPO DETECTED! Are you sure about this?')

print('Generating stimuli for participant', thisParticipant, 'at a BPM of', str(thisTempo))



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
			'Metro2HH']

# create participant folder

if not os.path.isdir('stims'):
	os.mkdir('stims')



#%% Cleaning

# delete all files in scratchFolders, so they don't sneak in.

scratchWavFiles = glob.glob('scratchWAV/*.wav')
for f in scratchWavFiles:
	os.remove(f)

scratchMidiFiles = glob.glob('scratchMIDI/*.mid')
for f in scratchMidiFiles:
	os.remove(f)	


# this may not remove all files
	
	

#%% Read midi, make wav
# there should be 16 files.

# Hardcoded stimuli MIDI
HR1HH3 = mido.MidiFile('stimMidi/HR1HH3.mid')
HR1MH2 = mido.MidiFile('stimMidi/HR1MH2.mid')
HR3HH5 = mido.MidiFile('stimMidi/HR3HH5.mid')
HR3MH4 = mido.MidiFile('stimMidi/HR3MH4.mid')
LR3HH3 = mido.MidiFile('stimMidi/LR3HH3.mid')
LR3MH2 = mido.MidiFile('stimMidi/LR3MH2.mid')
LR7HH3 = mido.MidiFile('stimMidi/LR7HH3.mid')
LR7MH4 = mido.MidiFile('stimMidi/LR7MH4.mid')
MariatoClaveMR5HH3 = mido.MidiFile('stimMidi/MariatoClaveMR5HH3.mid')
MariatoClaveMR5MH2 = mido.MidiFile('stimMidi/MariatoClaveMR5MH2.mid')
SonClaveMR1HH5 = mido.MidiFile('stimMidi/SonClaveMR1HH5.mid')
SonClaveMR1MH4 = mido.MidiFile('stimMidi/SonClaveMR1MH4.mid')
Metro1MH = mido.MidiFile('stimMidi/Metro1MH.mid')
Metro1HH = mido.MidiFile('stimMidi/Metro1HH.mid')
Metro2MH = mido.MidiFile('stimMidi/Metro2MH.mid')
Metro2HH = mido.MidiFile('stimMidi/Metro2HH.mid')

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
			Metro2HH]

# run through, change tempo, make .wav-file

for n, thisStim in enumerate(allMidi):
	tempoChanged = change_tempo(thisStim, thisTempo)
	saveNameMidi = 'scratchMIDI/' + listLevels[n] + '.mid'
	tempoChanged.save(saveNameMidi)
	saveNameWav = 'scratchWAV/' + listLevels[n] + '.wav'
	write_wav(saveNameMidi, saveNameWav)
	


#%% Generate audio for experiment 1

# read in silence-file
fs, silence = wavfile.read('staticWAV/silence10s.wav')
length = silence.shape[0]/fs


# calculate length of repeat in samples
samplesRepeat = math.floor(repeatTime * fs)

# now stich together according to randomized order.
# also make a .txt-file with information
condArray = ['silence']
timeArray = [0]

outputWav = silence
for n, condition in enumerate(randomizedOrder):
	condArray.append(condition)
	currLength = len(outputWav)/fs
	timeArray.append(currLength)
	thisStimName = 'scratchWAV/'+condition+'.wav'
	fs, thisStim = wavfile.read(thisStimName)
	thisStim = thisStim[0:samplesRepeat]
	thisBlock = np.tile(thisStim, [blockReps,1])
	outputWav = np.append(outputWav, thisBlock, axis=0)
	currLength = len(outputWav)/fs
	timeArray.append(currLength)
	condArray.append('silence')
	outputWav = np.append(outputWav, silence, axis=0)


# write audio
participantAudio = thisPartFolder + '/' + thisParticipant + '_experiment1.wav'	
wavfile.write(participantAudio, fs, outputWav)

participantLogName = thisPartFolder + '/' + thisParticipant + '_experiment1.csv'

totalLengthExp1 = (outputWav.shape[0]/fs)
minutes = math.floor(totalLengthExp1/60)
seconds = math.floor(totalLengthExp1 % 60)
print('Length of experiment 1:', minutes, 'm', seconds, 's')

# write log
logDict = {'Condition': condArray, 'Time': timeArray}
logDF = pd.DataFrame(data=logDict)
logDF.to_csv(participantLogName)


#%% Finished.
print('Now finished.')
