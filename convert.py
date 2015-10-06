#!/usr/bin/env python

import pprint
print = pprint.pprint

import sys
import math
from copy import copy

from utils import absolute2relative

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
divisions = int(attributes.find('divisions').text)
# print(divisions)
#time_signature = attributes.find('./time') # TODO: save time signature data

note_queue = []
key_signature_list = []
beat_counter = 0
tie_start = False

# import pdb;pdb.set_trace()

for measure in part_angklung:
    for child in measure:
        if child.tag == 'attributes':
            if child.find('key/fifths') is not None:
                key_signature_list.append({
                    'key_signature': int(child.find('key/fifths').text),
                    'position': beat_counter
                    })

        elif child.tag == 'note':
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

            new_note['duration'] = int(note.find('duration').text)
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
            beat_counter -= int(child.find('duration').text)

# print(note_queue, width=100, compact=True)
# print(key_signature_list, width=100, compact=True)
# print(beat_counter)
# sys.exit()

music_score = [[]]
for i in range(beat_counter):
    music_score[0].append(0)

while note_queue:
    note = note_queue.pop()
    if note['type'] == 'pitch':
        line = 0
        while music_score[line][note['position']] != 0:
            line += 1
            try:
                music_score[line]
            except IndexError:
                music_score.append([])
                for i in range(beat_counter):
                    music_score[line].append(0)
        for i in range(len(key_signature_list) - 1, -1, -1):
            if note['position'] >= key_signature_list[i]['position']:
                keysig = key_signature_list[i]['key_signature']
                break
        else:
            raise Exception('key signature not found')
        for i in range(note['position'], note['position'] + note['duration']):
            music_score[line][i] = absolute2relative(keysig, note['step'], note['alter'], note['octave'])

print(music_score, width=100, compact=True)
