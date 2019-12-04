'''
	Prints all stock symbols in NASDAQ 100 as a list of lists of size N
'''

import re
import json


if __name__ == "__main__":
	
	N = 8

	filepath = 'nasdaq100list.txt'
	pattern = re.compile('\S*')
	with open(filepath) as file:
		symbol_batches = []
		curr_symbol_batch = []
		for i, line in enumerate(file):
			# split symbol list into lists of size N for API request
			if ((i % N == 0) and i != 0) or i == 99:
				symbol_batches.append(curr_symbol_batch)
				curr_symbol_batch = []

			# find the symbol on the current line
			match = pattern.match(line)
			if match:
				curr_symbol_batch.append(match.group(0))

	print(symbol_batches)
