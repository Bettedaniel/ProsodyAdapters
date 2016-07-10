from argparse import ArgumentParser
import modules.filesUtility as filesUtility
from modules.Helpers import createFile
import modules.bcolors as bcolors
from modules.Helpers import extractWord, findColumn, loadWorksheet, makeMappingFromFileToPath
from pydub import AudioSegment
import os
import os.path as op
import xlrd

# We want this file size approximately, in Bytes.
approxFileSize = 5000000

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
	targetDirectory = "directories/SplitMonos/"
	filesUtility.createDirectory(targetDirectory)
	for key in transcriptions:
		file = op.join(monos, key+".wav")
		if not op.isfile(file):
			continue
		sound = AudioSegment.from_wav(file)
		size = op.getsize(file)
		splitTimes = []
		if (size <= 1.5 * approxFileSize):
			print ("File too small for meaningful split.")
		else:
			numberOfSplits = int(size / approxFileSize)
			soundDuration = len(sound)
	#		print ("Number of splits: %s" % (numberOfSplits))
			approxLength = int(soundDuration / (numberOfSplits+1))
			splitTimes = splitSingleMono(approxLength, transcriptions[key])
		if (len(splitTimes) == 0):
			# No splits.
			print ("No splits.")
			sound.export(targetDirectory + key + ".wav", format="wav")
		else:
			previousSplit = 0
			segments = []
			for splitPoint in splitTimes:
				mSec = int(round(splitPoint * 1000.0))
				segments.append(sound[previousSplit:mSec])
				previousSplit = mSec
			segments.append(sound[previousSplit:len(sound)])
			for i in range(0, len(segments)):
				segments[i].export(targetDirectory + key + str(i) + ".wav", format="wav")
		createLabels(targetDirectory+key, splitTimes, transcriptions[key])

def createLabels(fileName, splitTimes, triples):
	currentSplit = 0
	label = ""
	previousEnd = 0
	for triple in triples:
		start = triple[1]
		end = triple[1] + triple[2]
		if len(splitTimes) > currentSplit and splitTimes[currentSplit] <= start and splitTimes[currentSplit] >= previousEnd:
			writeFile(fileName+str(currentSplit)+".lab", label[1:])
					
			currentSplit += 1
			label = ""
		label = label + " " + (" ".join(triple[0]).upper())
		previousEnd = end

#	print (currentSplit)
	if currentSplit == 0:
		writeFile(fileName+".lab", label[1:])
	else:
		writeFile(fileName+str(currentSplit)+".lab", label[1:])
	
def writeFile(filePath, text):
	with open(filePath, "w+") as f:
		f.write(text)
	

def splitSingleMono(approxLength, triples):
	endOfNext = approxLength / float(1000)
	toSplitTimes = []
	previousEnd = 0
	for triple in triples:
		start = triple[1]
		end = triple[1] + triple[2]
		if (start >= endOfNext):
			if canSplit(previousEnd, start):
				splitPoint = previousEnd + ((start - previousEnd) / 2.0)
				toSplitTimes.append(splitPoint)
				endOfNext += (approxLength / float(1000))
		previousEnd = end
	return toSplitTimes
		
def canSplit(previousEnd, currentStart):
	return (currentStart - previousEnd) > 0.005


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

