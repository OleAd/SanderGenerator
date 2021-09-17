# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 12:00:38 2021

@author: olehe

This should generate audio for Sander's experiment
Only one repeat, and at given BPM.


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
	fluidsynth = 'C:/Users/olehe/Documents/GitHub/VPD_generator/fluidsynth-2.2.2/bin/fluidsynth.exe'
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


# total length of experiment, could be used as a ceiling measure.
totalLength = 20*60

# one block means on block of listening to a stimuli
blockLength = 30

# how many times to repeat blocks (not sequentially, but throughout the experiment)
# currently not used
#blockRepeats = 2

# Calculate number of repeats per block
# one repeat is TWO bars

barTime = (60/thisTempo)*4
repeatTime = barTime * 2

#note: this aims at 60 seconds long blocks.

# number of times to repeat a stimuli within a block
blockReps = math.floor(blockLength/barTime)


# levels of our stimuli, in order.
listLevels = ['IL', 'IM', 'IH',
			  'LL', 'LM', 'LH',
			  'ML', 'MM', 'MH',
			  'HL', 'HM', 'HH']

# randomize order for experiment 1
randomizedOrder = random.sample(listLevels, len(listLevels))

# create participant folder

if not os.path.isdir('participants'):
	os.mkdir('participants')

thisPartFolder = 'participants/' + thisParticipant

if not os.path.isdir(thisPartFolder):
	os.mkdir(thisPartFolder)

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


# Hardcoded stimuli MIDI
IL = mido.MidiFile('stimMIDI/01a_CL.mid')
IM = mido.MidiFile('stimMIDI/01b_CM.mid')
IH = mido.MidiFile('stimMIDI/01c_CH.mid')
LL = mido.MidiFile('stimMIDI/02_LL-LR3LH2.mid')
LM = mido.MidiFile('stimMIDI/05_LM-LR3MH2.mid')
LH = mido.MidiFile('stimMIDI/08_LH-LR3HH5.mid')
ML = mido.MidiFile('stimMIDI/29_ML-MR1LH3.mid')
MM = mido.MidiFile('stimMIDI/32_MM-MR1MH2.mid')
MH = mido.MidiFile('stimMIDI/35_MH-MR1HH5.mid')
HL = mido.MidiFile('stimMIDI/56_HL-HR1LH3.mid')
HM = mido.MidiFile('stimMIDI/59_HM-HR1MH2.mid')
HH = mido.MidiFile('stimMIDI/62_HH-HR1HH5.mid')

allMidi = [IL, IM, IH,
		   LL, LM, LH,
		   ML, MM, MH,
		   HL, HM, HH]

# run through, change tempo, make .wav-file

for n, thisStim in enumerate(allMidi):
	tempoChanged = change_tempo(thisStim, thisTempo)
	saveNameMidi = 'scratchMIDI/' + listLevels[n] + '.mid'
	tempoChanged.save(saveNameMidi)
	#time.sleep(1)
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


#%% Generate audio for experiment 2

# note, we're here using the original order
strictlyOrdered = listLevels
	
fs, silence = wavfile.read('staticWAV/silence10s.wav')
length = silence.shape[0]/fs


# calculate length of repeat in samples
samplesRepeat = math.floor(repeatTime * fs)

# now stich together according to randomized order.
# also make a .txt-file with information
condArray = ['silence']
timeArray = [0]

outputWav = silence
for n, condition in enumerate(strictlyOrdered):
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
participantAudio = thisPartFolder + '/' + thisParticipant + '_experiment2.wav'	
wavfile.write(participantAudio, fs, outputWav)

totalLengthExp2 = (outputWav.shape[0]/fs)
minutes = math.floor(totalLengthExp2/60)
seconds = math.floor(totalLengthExp2 % 60)
print('Length of experiment 2:', minutes, 'm', seconds, 's')

participantLogName = thisPartFolder + '/' + thisParticipant + '_experiment2.csv'

# write log
logDict = {'Condition': condArray, 'Time': timeArray}
logDF = pd.DataFrame(data=logDict)
logDF.to_csv(participantLogName)


#%% Finished.
print('Now finished.')
