relative_list = ['Z', 'S', 'X', 'D', 'C', 'V', 'G', 'B', 'H', 'N', 'J', 'M', # 1rr .. 7rr
			 'z', 's', 'x', 'd', 'c', 'v', 'g', 'b', 'h', 'n', 'j', 'm', # 1r .. 7r
			 'q', '2', 'w', '3', 'e', 'r', '5', 't', '6', 'y', '7', 'u', # 1 .. 7
			 'Q', '@', 'W', '#', 'E', 'R', '%', 'T', '^', 'Y', '&', 'U', # 1t .. 7t
			 'I', '(', 'O', ')', 'P', '{', '+', '}'] # 1tt .. 5tt

step_list = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def absolute2relative(keysig, step, alter, octave):
	# add typechecks to args!
	# keysig??
	numeral_value = step_list.index(step)
	numeral_value += alter
	numeral_value += octave * 12
	numeral_value -= 24 # karena Cgajah paling rendah
	return relative_list[numeral_value]

if __name__ == '__main__':
	import sys

	n = absolute2relative(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
	print(n)