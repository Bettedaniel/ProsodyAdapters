from argparse import ArgumentParser
import modules.bcolors as bcolors
from modules.Helpers import extractWord, findColumn, loadWorksheet, makeMappingFromFileToPath
from pydub import AudioSegment
import os
import os.path as op
import xlrd

def extractMonologueData(sheets):
	transcriptions = dict()
	words = []
	phonetics = dict()
	for sheet in sheets:
		pos_column = findColumn(sheet, 'PoS')
		lydskrift_column = findColumn(sheet, 'idealiseret lydskrift')	
		time_column = findColumn(sheet, 'tid')
		duration_column = findColumn(sheet, 'varighed')
		for row in range(sheet.nrows):
			if (row == 0):
				continue
			fileName = sheet.cell(row, 0).value
			word = extractWord(sheet.cell(row, pos_column).value)
			phones = (sheet.cell(row, lydskrift_column).value).split()
			time = float(sheet.cell(row, time_column).value)
			duration = float(sheet.cell(row, duration_column).value)
			if word and phones:
				transcriptions.setdefault(fileName, []).append((word, time, duration))
				phonetics.setdefault(fileName, []).append((word, phones))
				for w in word:
					if w not in words:
						words.append(w)
	return words, transcriptions, phonetics

def splitMonologues(danpass, monos):
	sheet = loadWorksheet(op.join(danpass, "monologues.xlsx"))
	words, transcriptions, phonetics = extractMonologueData([sheet])
			
	for key in transcriptions:
		file = op.join(monos, key+".wav")
		sound = AudioSegment.from_wav(file)
		size = op.getsize(file)
		print ("File = %s, size = %s Bytes" % (file, size))
		print ("%s MBytes" % (size / float(1000000)))
		for triple in transcriptions[key]:
			print (triple)
	
"""
	We have all the puzzle pieces. Just need to split intelligently.
"""	



def main(danpass, monos, dials):
	bcolors.init()
	if not monos is None:
		splitMonologues(danpass, monos)


if __name__ == "__main__":
	argparser = ArgumentParser(description='Split .wav files.')
	argparser.add_argument('-d', help='Path to the DanPass corpus.')
	argparser.add_argument('-mono', help='Path to folder with to split monologue sound files.')
	argparser.add_argument('-dial', help='Path to folder with to split dialogue sound files.')
	
	args = argparser.parse_args()
	main(args.d, args.mono, args.dial)

