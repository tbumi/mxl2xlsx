#!/usr/bin/env python
# [SublimeLinter flake8-max-line-length:90 @python:3]

import pprint
# print = pprint.pprint

import sys
from copy import copy
from collections import deque

from utils import absolute2relative, keysig_int2str, keysig_int2angkl

import xlsxwriter
import xml.etree.ElementTree as ET
try:
    file_path = sys.argv[1]  # file path as first command line argument
except IndexError:
    sys.exit("Error: input musicXML file as first argument.")


mxml = ET.parse(file_path)
score_partwise = mxml.getroot()
# assume P1 is always angklung, (TODO: add check)
part_angklung = score_partwise.find('part')

attributes = part_angklung.find('measure/attributes')
divisions = int(attributes.find('divisions').text)
# print(divisions)
# time_signature = attributes.find('./time') # TODO: save time signature data

note_queue = []
key_signature_list = []
beat_counter = 0
tie_start = False
tie_note = {}
num_of_staffs = 1

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
            note = child  # for easier code reading
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
                    old_duration = new_note['duration']
                    new_note = copy(tie_note)
                    new_note['duration'] = old_duration + tie_note['duration']
                    tie_start = False
                if tie_tag.get('type') == 'start':
                    tie_note = copy(new_note)
                    tie_start = True
            if tie_start:
                continue

            if note.find('chord') is not None:
                beat_counter -= new_note['duration']

            new_note['position'] = beat_counter

            if note.find('staff') is not None:
                staff = int(note.find('staff').text)
                new_note['staff'] = staff - 1
                if staff > num_of_staffs:
                    num_of_staffs = staff
            else:
                new_note['staff'] = 0

            note_queue.append(new_note)
            beat_counter += new_note['duration']

        elif child.tag == 'backup':
            beat_counter -= int(child.find('duration').text)

# print(note_queue, width=100, compact=True)
# print(key_signature_list, width=100, compact=True)
# print(beat_counter)
# sys.exit()

# print(num_of_staffs)
music_score_grid = []  # music_score > staff > line
for i in range(num_of_staffs):
    music_score_grid.append([deque()])
    for j in range(beat_counter):
        music_score_grid[i][0].append(0)

while note_queue:
    note = note_queue.pop()
    if note['type'] == 'pitch':
        staff = note['staff']
        line = 0
        empty = True
        for i in range(note['position'], note['position'] + note['duration']):
            if music_score_grid[staff][line][i] != 0:
                empty = False
        while not empty:
            empty = True
            line += 1
            try:
                music_score_grid[staff][line]
            except IndexError:
                music_score_grid[staff].append(deque())
                for i in range(beat_counter):
                    music_score_grid[staff][line].append(0)
            else:
                for i in range(note['position'], note['position'] + note['duration']):
                    if music_score_grid[staff][line][i] != 0:
                        empty = False

        for i in range(len(key_signature_list) - 1, -1, -1):
            if note['position'] >= key_signature_list[i]['position']:
                keysig = key_signature_list[i]['key_signature']
                break
        else:
            raise Exception('key signature not found')

        for i in range(note['position'], note['position'] + note['duration']):
            if i == note['position']:
                music_score_grid[staff][line][i] = absolute2relative(
                    keysig, note['step'], note['alter'], note['octave'])
            else:
                music_score_grid[staff][line][i] = '.'

# print(music_score_grid, width=95, compact=True)
# pprint.pprint(music_score_grid, width=95, compact=True)
# sys.exit()

music_score_cells = []
line_counter = -1

# import pdb;pdb.set_trace()
for staff in music_score_grid:
    for line in staff:
        music_score_cells.append([])
        line_counter += 1
        note_string = ''
        note_duration = 0
        while line:
            duration = 1
            note = line.popleft()
            note_duration += 1
            while line and note_duration < divisions:
                if (note != 0 and line[0] == '.') or (note == 0 and line[0] == 0):
                    line.popleft()
                    duration += 1
                    note_duration += 1
                else:
                    break
            if duration/divisions == 1/4:
                note_string += '-=' + str(note)
            elif duration/divisions == 1/2:
                note_string += '-' + str(note)
            elif duration/divisions == 3/4:
                note_string += '-' + str(note) + '-=.'
            else:
                note_string = str(note)
            if note_duration == divisions:
                music_score_cells[line_counter].append(note_string)
                note_string = ''
                note_duration = 0

pprint.pprint(music_score_cells, width=95, compact=True)

workbook = xlsxwriter.Workbook('partitur.xlsx')
worksheet = workbook.add_worksheet()

partitur_format = workbook.add_format()
partitur_format.set_font_name('Partitur')
partitur_format.set_font_size(12)
partitur_format.set_align('center')
normal_text = workbook.add_format()
normal_text.set_font_name('Calibri')
normal_text.set_font_size(11)
normal_text.set_align('left')

row = 0
big_row = 0
lines_per_big_row = len(music_score_cells) + 1
col_counter = 0
beat_counter = 0

MAX_COLS = 4
COLUMN_WIDTH = 4

for line in music_score_cells:
    for cell in line:
        for ks in key_signature_list:
            if ks['position'] == beat_counter:
                if row != 0:
                    row += 1
                worksheet.write(
                    row, 0,
                    'Do = {} (no. {})'.format(keysig_int2str(ks['key_signature']),
                                              keysig_int2angkl(ks['key_signature'])),
                    normal_text
                )
                row += 1
                col_counter = 0
        worksheet.set_column(col_counter, col_counter, COLUMN_WIDTH, partitur_format)
        worksheet.write(row + (big_row * lines_per_big_row), col_counter, cell)
        if col_counter >= MAX_COLS - 1:
            col_counter = 0
            big_row += 1
        else:
            col_counter += 1
        beat_counter += 1
    col_counter = 0
    row += 1

workbook.close()
