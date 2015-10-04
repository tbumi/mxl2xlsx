#!/usr/bin/env python

import sys
import math
from collections import deque

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

# import pdb;pdb.set_trace()

for note in part_angklung.findall('measure/note'):
    if note.find('pitch') is not None:
        step = note.find('pitch/step').text
        try:
            alter = note.find('pitch/alter').text
        except AttributeError:
            alter = '0'
        octave = note.find('pitch/octave').text
    elif note.find('rest') is not None:
        step = '0'
        alter = ''
        octave = ''
    else:
        # import pdb;pdb.set_trace()
        sys.exit("Invalid MusicXML")

    duration = float(note.find('duration').text)/divisions
    if note.find('dot'):
        duration *= 1.5

    tie_tags = note.findall('tie')
    for tie_tag in tie_tags:
        if tie_tag.get('type') == 'stop':
            (step, alter, octave, duration_prev) = tie_note
            duration += duration_prev
        if tie_tag.get('type') == 'start':
            tie_note = (step, alter, octave, duration)
            continue

    note_queue.append((step, alter, octave, duration))

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
