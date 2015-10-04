#!/usr/bin/env python

import sys
import math
from collections import deque
from copy import copy

import xlsxwriter
import xml.etree.ElementTree as ET
try:
    file_path = sys.argv[1] # file path as first command line argument
except IndexError:
    sys.exit("Error: input musicXML file as first argument.")


mxml = ET.parse(file_path)
score_partwise = mxml.getroot()
#assume P1 is always angklung, (TODO: add check)
part_angklung = score_partwise.find('part')

attributes = part_angklung.find('measure/attributes')
divisions = float(attributes.find('divisions').text)
#key_signature = attributes.find('./key/fifths').text # TODO: handle key signature
#time_signature = attributes.find('./time') # TODO: save time signature

note_queue = deque()
beat_counter = 0
tie_start = False

# import pdb;pdb.set_trace()

for measure in part_angklung:
    for child in measure:
        if child.tag == 'note':
            note = child # for easier code reading
            new_note = {}

            if note.find('pitch') is not None:
                new_note['type'] = 'pitch'
                new_note['step'] = note.find('pitch/step').text
                try:
                    new_note['alter'] = int(note.find('pitch/alter').text)
                except AttributeError:
                    new_note['alter'] = 0
                new_note['octave'] = int(note.find('pitch/octave').text)
            elif note.find('rest') is not None:
                new_note['type'] = 'rest'
            else:
                # import pdb;pdb.set_trace()
                sys.exit("Invalid MusicXML")

            new_note['duration'] = float(note.find('duration').text)/divisions
            if note.find('dot'):
                new_note['duration'] *= 1.5

            tie_tags = note.findall('tie')
            for tie_tag in tie_tags:
                if tie_tag.get('type') == 'stop':
                    new_note = copy(tie_note)
                    new_note['duration'] += tie_note['duration']
                if tie_tag.get('type') == 'start':
                    tie_note = copy(new_note)
                    tie_start = True
            if tie_start:
                continue

            if note.find('chord') is not None:
                beat_counter -= new_note['duration']

            new_note['position'] = beat_counter

            note_queue.append(new_note)
            beat_counter += new_note['duration']

        elif child.tag == 'backup':
            beat_counter -= float(child.find('duration').text)/divisions

print(note_queue)
sys.exit()

music_score = []
beat_duration = 0
beat = []
one_beat_duration = 1.0 # just to make clear wkwk

while note_queue:
    note = note_queue.popleft()
    step, alter, octave, duration = note
    if beat_duration + duration > one_beat_duration:
        new_beats = deque()
        remaining_duration = (beat_duration + duration) - one_beat_duration
        new_beats.appendleft((step, alter, octave, duration - remaining_duration))

        if step == '0':
            continuation = '0'
        else:
            continuation = '.'

        while remaining_duration > one_beat_duration:
            new_beats.appendleft((continuation, '', '', one_beat_duration))
            remaining_duration -= one_beat_duration
        if remaining_duration > 0:
            new_beats.appendleft((continuation, '', '', remaining_duration))
        note_queue.extendleft(new_beats)
        continue
    
    beat.append(note)
    beat_duration += duration
    if beat_duration == one_beat_duration:
        music_score.append(beat)
        beat = []
        beat_duration = 0

print(music_score)
