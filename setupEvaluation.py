from argparse import ArgumentParser
import modules.bcolors as bcolors
from modules.cleanTextgrids import createNew, createTextGrid, yankData
from modules.createDialogueLabels import getData, getTeams, createFileName
from modules.evaluate import getDictionary
from modules.evaluate import evaluate_skip_some, smart_evaluate
from modules.graphics import blockDiagram
from modules.Helpers import createFile, loadWorksheet
import os
import os.path as op
from modules.filesUtility import createDirectory, endOnSlash, getExtension
from setupTraining import dirParent, dirParams, dirDialRe
import textgrid
from textgrid import IntervalTier
from textgrid import TextGrid
import zipfile

"""
Unzip the danpass folders with the 'correct' TextGrids, and store them in <dirParent>/UnzippedCorrects/
"""
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

def createMonoWordTextGrids(danpass):
	monologues = endOnSlash(danpass) + 'monologues.xlsx'
	data = yankData(monologues)
	target = dirParent + '/WordGrids/monologues/'
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

def createDialWordTextGrids(danpass):
	dialogues = endOnSlash(danpass) + 'dialogues.xlsx'
	directory = dirParent+'/'+dirDialRe+'/'
	if not op.exists(directory):
		print ("%s'%s' does not exist. Maybe call setupTraining first?%s" % (bcolors.FAIL, directory, bcolors.ENDC))
		return
	target = dirParent + '/WordGrids/dialogues/'
	createDirectory(target)
	data = getData(loadWorksheet(dialogues))
	teams = getTeams(directory)
	
	textGridData = dict()
	for team in teams:
		mono1 = (team[0], team[2])
		mono2 = (team[1], team[2])
		both = (len(data[mono1]) > 0 and len(data[mono2]) > 0)
		if both:
			merge = [quad for quad in data[mono1]]
			for quad in data[mono2]:
				merge.append(quad)
			textGridData.setdefault(team, merge)
	
	TIME, DURATION, WORDS = 0, 1, 2  
	for team in teams:
		sortedList = sorted(textGridData[team], key=lambda tup: (tup[TIME], tup[DURATION]))
		sliceOfData = []
		fileName = createFileName(team)
		for quad in sortedList:
			sliceOfData.append((fileName, quad[TIME], quad[DURATION], quad[WORDS]))
		txtgrid = createTextGrid(sliceOfData)
		try:
			txtgrid.write(target+fileName+'.TextGrid')
			print ("%swrote '%s'%s" % (bcolors.OKGREEN, target+fileName+'.TextGrid', bcolors.ENDC))
		except:
			print ("%sError writing '%s'%s" % (bcolors.FAIL, target+fileName+'.TextGrid', bcolors.ENDC))
	return


"""
Available contains tuples of size 2 (despite the quad name), and each of these tuples contain two paths to folders containing .TextGrid files. We then compare every name matching .TextGrid file from one folder to the one in the other folder.
"""
def compareAll(available, closeness=0.02):
	results = []
	names = []
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
				results.append(result)
				names.append(file)
				print ("-----------\n%s\n%s\n%sResult=%.4f%s\n-----------" % (quad[0]+file, quad[1]+file, bcolors.OKGREEN, result, bcolors.ENDC))
				total = total + result
				amount = amount + 1
		print ("%s\nvs.\n%s" % (quad[0], quad[1]))
		print ("%sAverage result=%.4f%s" % (bcolors.OKBLUE, (total / float(amount)), bcolors.ENDC))
	return results, names

"""
Get all file names of files with the extension 'extension'.
"""
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

"""
Clean up the TextGrid file 'fileName' in directory 'sourceDirectory' and create a new clean .TextGrid file with the same file name in 'targetDirectory'.
"""
def doCleanUp(sourceDirectory, fileName, tierName, targetDirectory):
	txtgrid = TextGrid.fromFile(sourceDirectory+fileName)
	cleanTxtgrid = createNew(txtgrid, tierName)	
	cleanTxtgrid.write(targetDirectory+fileName)

"""
Create a new directory as 'path/CLEANED/' and return it.
"""
def createDirectoryWrapper(path):
	new_directory = ''
	if path[len(path)-1] == '/':
		new_directory = path[0:len(path)-1]
	else:
		new_directory = path
	new_directory = new_directory + 'CLEANED/'
	createDirectory(new_directory)
	return new_directory


def main(danPass, directories, compares):
	bcolors.init()
#	argparser = ArgumentParser(description="Setup textgrids for testing.")
#	argparser.add_argument('-f', '--fetch', type=str, help='Path to danpass set.')
#
#	argparser.add_argument('-d', '--dirs', nargs=2, action='append', help="Path to directory with .TextGrid files, and the tier name to fix.")
#
#	argparser.add_argument('-c', '--comp', nargs=2, action='append', help='Path to two .TextGrid directories which we will compare.')
#
#	args = argparser.parse_args()

#	danPass = args.fetch
	if not danPass is None:
		didUnzip = unzipCorrects(danPass)
		print ("%sCreate monologue 'correct' word .TextGrid files.%s" % (bcolors.BOLD, bcolors.ENDC))
		createMonoWordTextGrids(danPass)
		print ("%sCreate dialogue 'correct' word .TextGrid files.%s" % (bcolors.BOLD, bcolors.ENDC))
		createDialWordTextGrids(danPass)
#	directories = args.dirs
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
#	compares = args.comp
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
		results, names = compareAll(available)
		blockDiagram(ratios=results, names=names, graphName='results', overwrite=True, show=True)

	return 0

if __name__ == "__main__":
	argparser = ArgumentParser(description="Setup textgrids for testing.")
	argparser.add_argument('-f', '--fetch', type=str, help='Path to danpass set.')

	argparser.add_argument('-d', '--dirs', nargs=2, action='append', help="Path to directory with .TextGrid files, and the tier name to fix.")

	argparser.add_argument('-c', '--comp', nargs=2, action='append', help='Path to two .TextGrid directories which we will compare.')

	args = argparser.parse_args()

	main(args.fetch, args.dirs, args.comp)
