"""
Dialogue sound files are stereo and are split into two mono parts in our spreadsheet. We need to merge these two to get a single .lab file per dialogue sound file.
"""
import glob
from modules.Helpers import loadWorksheet, findColumn, createFile, extractWord
from argparse import ArgumentParser
import os.path as op

def removeExtension(file_='bla/bla/0_og_1_kort_2.wav'):
	# Make one split from the right.
	return file_.rsplit('.', 1)[0]

def getParts(file_='bla/bla/0_og_1_kort_2.wav'):
	file_ = removeExtension(file_)
	temp = file_.split('/')
	last = temp[len(temp) - 1]
	split = last.split('_')
	try:
		return (int(split[0]), int(split[2]), int(split[4]))
	except:
		print ("Not all integers: (%s, %s, %s)" % (split[0], split[2], split[4]))

def getTeams(path):
#	print (glob.glob(path+'/*.wav'))
	files = glob.glob(path+'/*.wav')
	teams = set()
	for file_ in files:	
		trip = getParts(file_)
		teams.add(trip)

	return teams

def getPersonAndMap(fileName='d_001_1_f_non-v'):
	parts = fileName.split('_')
	try:
		return (int(parts[1]), int(parts[2]))
	except:
		print ("Not integer: (%s, %s)" % (parts[1], parts[2]))

"""
Get the needed data from the dialogues spreadsheet.
"""
def getData(sheet):
	pos_column = findColumn(sheet, 'PoS')
	lydskrift_column = findColumn(sheet, 'lydskrift')
	time_column = findColumn(sheet, 'tid')
	duration_column = findColumn(sheet, 'varighed')
	data = dict()
	for row in range(1, sheet.nrows):
		fileName = sheet.cell(row, 0).value
		posWord = extractWord(sheet.cell(row, pos_column).value)
		phones = sheet.cell(row, lydskrift_column).value
		sTime = float(sheet.cell(row, time_column).value)
		dTime = float(sheet.cell(row, duration_column).value)
#		print ("@@@@@@@\n%s\n%s\n%s\n@@@@@@@" % (fileName, ortoWord, phones))
#		print (getPersonAndMap(fileName))
		
		# If the word exists and it can be pronounced.
		if posWord and phones:
			tup = getPersonAndMap(fileName)
			data.setdefault(tup, []).append((sTime, dTime, posWord, phones))
	
	return data

def createFileName(triple=(0,1,2)):
	return str(triple[0]) + '_og_' + str(triple[1]) + '_kort_' + str(triple[2]) 

def main():
	argparser = ArgumentParser(description="Create dialogues .lab files.")
	argparser.add_argument('-d', '--d', help='Path to folder with dialogue .wav files.')
	argparser.add_argument('-s', '--s', help='Path to the dialogues spreadsheet.')
	
	args = argparser.parse_args()

	createLabels(args.s, args.d, './dialogueLabs/')
#	teams = getTeams(args.d)
#	sheet = loadWorksheet(args.s)
#	data = getData(sheet)
#	merged = dict()
#	for trip in teams:
#		tup1 = (trip[0], trip[2])
#		tup2 = (trip[1], trip[2])
#		if (len(data[tup1]) > 0 and len(data[tup2]) > 0):
#			temp = [quad for quad in data[tup1]]
#			for quad in data[tup2]:
#				temp.append(quad)
#			merged.setdefault(trip, temp)
#	
#	for trip in merged:
#		list_ = sorted(merged[trip], key=lambda tup: (tup[0], tup[1]))
#		name = createFileName(trip)
#		label = ""
#		i = 0
#		for (a, b, word, d) in list_:
#			if (i == 0):
#				label = label + word.upper()
#			else:
#				label = label + " " + word.upper()
#			i = i + 1
#		createFile('./dialogueLabs/'+name, '.lab', [label], True)
	return 0

def createLabels(sheet_path, wavs, target):
	teams = getTeams(wavs)
	sheet = loadWorksheet(sheet_path)
	data = getData(sheet)
	merged = dict()
	for trip in teams:
		tup1 = (trip[0], trip[2])
		tup2 = (trip[1], trip[2])
		if (len(data[tup1]) > 0 and len(data[tup2]) > 0):
			temp = [quad for quad in data[tup1]]
			for quad in data[tup2]:
				temp.append(quad)
			merged.setdefault(trip, temp)
	
	for trip in merged:
		list_ = sorted(merged[trip], key=lambda tup: (tup[0], tup[1]))
		name = createFileName(trip)
		label = ""
		i = 0
		for (a, b, words, d) in list_:
			for word in words:
				if (i == 0):
					label = label + word.upper()
				else:
					label = label + " " + word.upper()
				i = i + 1
		createFile(target+name, '.lab', [label], True)
	return 0

if __name__ == "__main__":
	main()
