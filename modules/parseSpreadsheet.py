import xlrd
import argparse
import os.path as op

import modules.Helpers as Helpers

"""
Should change prints to logger actions.
"""

def main():
	parser = argparse.ArgumentParser(description='Process spreadsheet(s) to use the data with the prosodylab-alignment software.')
	parser.add_argument('sheets', metavar='Path', type=str, nargs='+', help='Path to a spreadsheet.')
#	parser.add_argument('-mono', '--mono', nargs=2, metavar=('PATH', 'COLUMN'), help='Path to monologues spreadsheet, and index of the pronounciation column.')
#	parser.add_argument('-dial', '--dial', nargs=2, metavar=('PATH', 'COLUMN'), help='Path to the dialogues spreadsheet, and index of the pronounciation column.')
	parser.add_argument('-dict', '--dict', dest='createDictionary', action='store_const', const=True, default=False, help='Create the dictionary')
	parser.add_argument('-map', '--map', dest='doMap', action='store_const', const=True, default=False, help='Map the phones to characters readable by the prosodylab-alignment software.')
	parser.add_argument('-label', '--label', dest='createLabels', action='store_const', const=True, default=False, help='Create the transcription .label files.')

	args = parser.parse_args()
	
	sheets = args.sheets
	print (sheets)

	worksheets = []
	for sheet in sheets:
		if (sheet is None):
			continue
		if (not op.isfile(sheet)):
			print ("Unable find: %s" % (sheet))
			print ("Removed %s from arguments." % (sheet))
		else:
			worksheets.append(Helpers.loadWorksheet(sheet))
	words, transcriptions, phonetics = Helpers.extractData(worksheets)	
	if (args.createDictionary == True):
	#	Helpers.createDictionary(phonetics, args.doMap)
		createDictionary(worksheets, args.doMap, './')
	if (args.createLabels == True):
		createLabels(worksheets)
#		fileToPathMap = Helpers.makeMappingFromFileToPath(worksheets, ['monoLabels', 'dialLabels'])
#		if len(fileToPathMap) == 0:
#			print ("Mapping failed.")
#			return
#		Helpers.createTranscriptions(transcriptions, fileToPathMap)
	return

def createDictionary(worksheets, path, doMap):
	words, transcriptions, phonetics = Helpers.extractData(worksheets)
	Helpers.createDictionary(phonetics, path, doMap)

def createLabels(worksheets, paths=['monoLabels', 'dialLabels']):
	words, transcriptions, phonetics = Helpers.extractData(worksheets)	
	fileToPathMap = Helpers.makeMappingFromFileToPath(worksheets, paths)
	if len(fileToPathMap) == 0:
		print ("Mapping failed.")
		return
	Helpers.createTranscriptions(transcriptions, fileToPathMap)

if __name__ == "__main__":
	main()
