from argparse import ArgumentParser
import modules.bcolors as bcolors
from modules.cleanTextgrids import createNew, createTextGrid, yankData
from modules.evaluate import getDictionary
from modules.evaluate import evaluate_skip_some, smart_evaluate
import os
import os.path as op
from modules.filesUtility import createDirectory
from setupTraining import dirParent
from setupTraining import dirParams
import textgrid
from textgrid import IntervalTier
from textgrid import TextGrid
import zipfile

def getExtension(file):
	if not '.' in file:
		return ''
	else:
		return file.rsplit('.', 1)[1]

def endOnSlash(directory):
	if directory[len(directory) - 1] == '/':
		return directory
	return directory + '/'

def unzipCorrects(directory):
	if not op.exists(directory):
		print ("%s'%s' does not exist.%s" % (bcolors.FAIL, directory, bcolors.ENDC))
		return 0
	directory = endOnSlash(directory) + 'textgrids_2014.zip'
	createDirectory(dirParent)
	target = dirParent + '/UnzippedCorrects/'
	if op.exists(target):
		print ("%s'%s' already exists. Maybe already unzipped?%s" % (bcolors.WARNING, target, bcolors.ENDC))
		return False
	else:
		zipped = zipfile.ZipFile(directory)
		zipped.extractall(target)
		print ("%sExtracted '%s' to '%s'%s" % (bcolors.OKGREEN, directory, target, bcolors.ENDC))
		return True

def createWordTextGrids(danpass, spreadsheet='monologues.xlsx'):
	danpass = endOnSlash(danpass)
	data = yankData(danpass+spreadsheet)
	monoOrDial = spreadsheet.rsplit('.', 1)[0]
	target = dirParent + '/WordGrids/'+monoOrDial+'/'
	createDirectory(target)
	i = 0
	while i < len(data):
		j = i
		sliceOfData = []
		while (j < len(data) and data[i][0] == data[j][0]): 
			sliceOfData.append(data[j])
			j += 1
		txtgrid = createTextGrid(sliceOfData)
		try:
			txtgrid.write(target+data[i][0]+'.TextGrid')
			print ("%swrote '%s'%s" % (bcolors.OKGREEN, target+data[i][0]+'.TextGrid', bcolors.ENDC))
		except:
			print ("%sError writing '%s'%s" % (bcolors.FAIL, target+data[i][0]+'.TextGrid', bcolors.ENDC))
		i = j
	return 

def main():
	bcolors.init()
	argparser = ArgumentParser(description="Setup textgrids for testing.")
#	argparser.add_argument('Textgrid directories', metavar='P', type=str, nargs='+', help='Path to a directory with .TextGrid files that need cleaning.')

#	argparser.add_argument('-t', '--t', type=str, default='words', help='Tier to fix.')
	argparser.add_argument('-f', '--fetch', type=str, help='Path to danpass set.')

	argparser.add_argument('-d', '--dirs', nargs=2, action='append', help="Path to directory with .TextGrid files, and the tier name to fix.")

	argparser.add_argument('-c', '--comp', nargs=2, action='append', help='Path to two .TextGrid directories which we will compare.')

	args = argparser.parse_args()

	danPass = args.fetch
	if not danPass is None:
		didUnzip = unzipCorrects(danPass)
		print ("%sCreate 'correct' word .TextGrid files.%s" % (bcolors.BOLD, bcolors.ENDC))
		createWordTextGrids(danPass)
		# TODO Should also create word TextGrids for the dialogues.
	directories = args.dirs
	if not directories is None:
		available = []
		for dir in directories:
			dir[0] = endOnSlash(dir[0])
			tup = tuple(dir)
			if op.exists(tup[0]):
				available.append(tup)
			else:
				print ("%s'%s' does not exist.%s" % (bcolors.FAIL, tup[0], bcolors.ENDC))
		print (available)
		cleanAll(available)
	compares = args.comp
	if not compares is None:
		available = []
		for quad in compares:
			quad[0] = endOnSlash(quad[0])
			quad[1] = endOnSlash(quad[1])
			quadTup = tuple(quad)
			if op.exists(quadTup[0]) and op.exists(quadTup[1]):
				available.append(quadTup)
			else:
				print ("%s'%s' or '%s' does not exist.%s" % (bcolors.FAIL, quadTup[0], quadTup[1], bcolors.ENDC))
		print (available)
		compareAll(available)

	return 0

def compareAll(available, closeness=0.02):
	dictionary = getDictionary(dirParent + '/' + dirParams + '/dictionaryDKMapped1.dict')
	for quad in available:
		list1 = getWithExtension(quad[0], 'TextGrid')
		list2 = getWithExtension(quad[1], 'TextGrid')
		total = 0
		amount = 0
		for file in list1:
			if file in list2:
				first = TextGrid.fromFile(quad[0]+file)
				second = TextGrid.fromFile(quad[1]+file)
#				result = evaluate_skip_some(first, second, dictionary, closeness)
				result = smart_evaluate(first, second, closeness)
				print ("-----------\n%s\n%s\n%sResult=%.4f%s\n-----------" % (quad[0]+file, quad[1]+file, bcolors.OKGREEN, result, bcolors.ENDC))
				total = total + result
				amount = amount + 1
		print ("%s\nvs.\n%s" % (quad[0], quad[1]))
		print ("%sAverage result=%.4f%s" % (bcolors.OKBLUE, (total / float(amount)), bcolors.ENDC))

def getWithExtension(directory, extension):
	result = []
	for subdir, dirs, files in os.walk(directory):
		for file in files:
			ext = getExtension(file)
			if ext == extension:
				result.append(file)
	return result



"""
Available is a list of tuples (sourceDirectory, tierName)
Where sourceDirectory contains the .TextGrid files, and tierName is the name of the tier we want to clean.
"""
def cleanAll(available):
		TARGET = 'CLEANED/'
		for tup in available:
			createDirectory(tup[0]+TARGET)
			for subdir, dirs, files in os.walk(tup[0]):
				for file in files:
					ext = getExtension(file)
					if ext == 'TextGrid':
						doCleanUp(tup[0], file, tup[1], tup[0]+TARGET)

def doCleanUp(sourceDirectory, fileName, tierName, targetDirectory):
	txtgrid = TextGrid.fromFile(sourceDirectory+fileName)
	cleanTxtgrid = createNew(txtgrid, tierName, False)	
	cleanTxtgrid.write(targetDirectory+fileName)

def createDirectoryWrapper(path):
	new_directory = ''
	if path[len(path)-1] == '/':
		new_directory = path[0:len(path)-1]
	else:
		new_directory = path
	new_directory = new_directory + 'CLEANED/'
	createDirectory(new_directory)
	return new_directory

if __name__ == "__main__":
	main()
