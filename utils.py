relative_list = ['Z', 'S', 'X', 'D', 'C', 'V', 'G', 'B', 'H', 'N', 'J', 'M', # 1rr .. 7rr
				 'z', 's', 'x', 'd', 'c', 'v', 'g', 'b', 'h', 'n', 'j', 'm', # 1r .. 7r
				 'q', '2', 'w', '3', 'e', 'r', '5', 't', '6', 'y', '7', 'u', # 1 .. 7
				 'Q', '@', 'W', '#', 'E', 'R', '%', 'T', '^', 'Y', '&', 'U', # 1t .. 7t
				 'I', '(', 'O', ')', 'P', '{', '+', '}'] # 1tt .. 5tt

step_list = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
step_keysig_list = ['G', 'G#', 'A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#']
keysig_list = ['B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']

def absolute2relative(keysig, step, alter, octave):
	numeral_value = step_list.index(step) + 1
	numeral_value += octave * 12
	numeral_value += alter
	numeral_value -= 24 # karena Cgajah paling rendah

	numeral_value -= step_keysig_list.index(keysig_int2str(keysig)) - 5
	return relative_list[numeral_value - 1]

def keysig_int2str(keysig):
	return keysig_list[keysig + 7]

def keysig_int2angkl(keysig):
	return step_keysig_list.index(keysig_int2str(keysig)) + 1

if __name__ == '__main__':
	# import sys
	# n = absolute2relative(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
	# print(n)

	assert absolute2relative(0, 'C', 0, 2) == 'Z'
	assert absolute2relative(0, 'C', 0, 4) == 'q'
	assert absolute2relative(0, 'D', 0, 4) == 'w'
	assert absolute2relative(0, 'D', 1, 4) == '3'
	assert absolute2relative(0, 'B', -1, 4) == '7'
	assert absolute2relative(-5, 'C', 0, 4) == 'm'
	assert absolute2relative(1, 'C', 0, 4) == 'r'
