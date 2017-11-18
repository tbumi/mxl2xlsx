from collections import deque

from mxl2xlsx.utils import absolute2relative
from mxl2xlsx.utils import keysig_int2str, keysig_int2angkl

MAX_COLS = 20


def parse_mxl(mxml):
    score_partwise = mxml.getroot()
    if score_partwise.tag != 'score-partwise':
        raise ValueError("Only accepts MusicXML in score-partwise format.")
    # assume P1 is always angklung
    part_angklung = score_partwise.find('part')

    attributes = part_angklung.find('measure/attributes')
    divisions = int(attributes.find('divisions').text)

    note_queue = []
    key_signature_list = {}
    time_signature_list = []
    beat_counter = 0
    num_of_staffs = 1

    tie_notes = {}

    for measure in part_angklung:
        for child in measure:
            if child.tag == 'attributes':
                if child.find('key/fifths') is not None:
                    key_signature_list[beat_counter//divisions] = \
                        int(child.find('key/fifths').text)
                if child.find('time/beats') is not None:
                    time_signature_list.append({
                        'beats': int(child.find('time/beats').text),
                        'position': beat_counter//divisions
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
                    raise ValueError("Invalid MusicXML")

                new_note['duration'] = int(note.find('duration').text)
                if note.find('dot'):
                    new_note['duration'] *= 1.5

                if note.find('staff') is not None:
                    staff = int(note.find('staff').text)
                    new_note['staff'] = staff - 1
                    if staff > num_of_staffs:
                        num_of_staffs = staff
                else:
                    new_note['staff'] = 0

                if note.find('chord') is not None:
                    beat_counter -= new_note['duration']

                new_note['position'] = beat_counter
                beat_counter += new_note['duration']

                tie_tags = note.findall('tie')
                is_tie_start = False
                for tie_tag in tie_tags:
                    note_id = '{}:{}{}{}'.format(
                        new_note['staff'], new_note['step'],
                        new_note['alter'], new_note['octave'])
                    if tie_tag.get('type') == 'stop':
                        old_duration = new_note['duration']
                        new_note = tie_notes[note_id].copy()
                        new_note['duration'] = old_duration + new_note['duration']
                    if tie_tag.get('type') == 'start':
                        tie_notes[note_id] = new_note.copy()
                        is_tie_start = True

                if not is_tie_start:
                    note_queue.append(new_note)

            elif child.tag == 'backup':
                beat_counter -= int(child.find('duration').text)

    music_score_grid = []  # music_score > staff > line
    for i in range(num_of_staffs):
        music_score_grid.append([deque()])
        for j in range(beat_counter):
            music_score_grid[i][0].append('0')

    while note_queue:
        note = note_queue.pop()
        if note['type'] == 'pitch':
            staff = note['staff']
            line = 0
            empty = True
            for i in range(note['position'], note['position'] + note['duration']):
                if music_score_grid[staff][line][i] != '0':
                    empty = False
                    break
            while not empty:
                empty = True
                line += 1
                try:
                    music_score_grid[staff][line]
                except IndexError:
                    music_score_grid[staff].append(deque())
                    for i in range(beat_counter):
                        music_score_grid[staff][line].append('0')
                else:
                    for i in range(note['position'], note['position'] + note['duration']):
                        if music_score_grid[staff][line][i] != '0':
                            empty = False

            for pos in sorted(key_signature_list.keys(), reverse=True):
                if note['position']//divisions >= pos:
                    keysig = key_signature_list[pos]
                    break
            else:
                raise ValueError('key signature not found')

            for i in range(note['position'], note['position'] + note['duration']):
                if i == note['position']:
                    music_score_grid[staff][line][i] = absolute2relative(
                        keysig, note['step'], note['alter'], note['octave'])
                else:
                    music_score_grid[staff][line][i] = '.'

    music_score_cells = []
    line_counter = -1

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
                    if (note != '0' and line[0] == '.') or \
                            (note == '0' and line[0] == '0'):
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

    lines_per_big_row = len(music_score_cells) + 1
    time_signature_queue = deque(time_signature_list)
    cur_time_signature = 4

    excel_grid = []

    for line_num, line_entries in enumerate(music_score_cells):
        big_row = 0
        col_counter = 0
        offset = 2
        cur_beat = 0
        while cur_beat < len(line_entries):
            cur_row = line_num + (big_row * lines_per_big_row) + offset

            if cur_beat in key_signature_list:
                if col_counter != 0:
                    col_counter = 0
                    big_row += 1
                    cur_row = line_num + (big_row * lines_per_big_row) + offset
                if line_num == 0:
                    keysig_str = keysig_int2str(key_signature_list[cur_beat])
                    keysig_noang = keysig_int2angkl(key_signature_list[cur_beat])
                    while len(excel_grid) <= cur_row:
                        excel_grid.append([])
                    while len(excel_grid[cur_row]) <= col_counter:
                        excel_grid[cur_row].append('')
                    excel_grid[cur_row][col_counter] = {
                        'text': f'Do = {keysig_str} (no. {keysig_noang})',
                        'format': 'normal'
                    }
                offset += 1
                cur_row = line_num + (big_row * lines_per_big_row) + offset

            cell = {}
            if time_signature_queue and time_signature_queue[0]['position'] == cur_beat:
                ts = time_signature_queue.popleft()
                cur_time_signature = ts['beats']
                cell['format'] = 'partitur_lborder'
            elif col_counter == 0 and cur_beat % cur_time_signature == 0:
                cell['format'] = 'partitur_lborder'
            elif (cur_beat + 1) % cur_time_signature == 0:
                cell['format'] = 'partitur_rborder'
            else:
                cell['format'] = 'partitur'

            while len(excel_grid) <= cur_row:
                excel_grid.append([])
            while len(excel_grid[cur_row]) <= col_counter:
                excel_grid[cur_row].append('')

            cell['text'] = line_entries[cur_beat]
            excel_grid[cur_row][col_counter] = cell

            if col_counter >= MAX_COLS - 1 or \
                    (cur_beat + 1) % cur_time_signature == 0 and \
                    col_counter + cur_time_signature >= MAX_COLS - 1:
                col_counter = 0
                big_row += 1
            else:
                col_counter += 1
            cur_beat += 1

    return excel_grid
