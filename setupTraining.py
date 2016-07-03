"""
Setup training. Requires the prosodylab-aligner to be already installed.
Requires Unix system.
"""
from argparse import ArgumentParser
import modules.bcolors as bcolors
import modules.createDialogueLabels as createDialogueLabels
from modules.createYaml import createYaml
from modules.Helpers import loadWorksheet, createFile
import os.path as op
import os
import modules.parseSpreadsheet as parseSpreadsheet
from random import shuffle
import shutil
from subprocess import call
import zipfile
from modules.filesUtility import createDirectory, getExtension, removeExtension, removeFolder, extensionCheck, getFiles, transferFiles, check_same

#class bcolors:
#	HEADER = '\033[95m'
#	OKBLUE = '\033[94m'
#	OKGREEN = '\033[92m'
#	WARNING = '\033[93m'
#	FAIL = '\033[91m'
#	ENDC = '\033[0m'
#	BOLD = '\033[1m'
#	UNDERLINE = '\033[4m'

dirMonoRe = 'MonoResampled'
dirDialRe = 'DialResampled'
dirMonoLabs = 'MonoLabels'
dirDialLabs = 'DialLabels'
dirDialTrain = 'DialTrain'
dirDialTest = 'DialTest'
dirMonoTrain = 'MonoTrain'
dirMonoTest = 'MonoTest'
dirAllTrain = 'AllTrain'
dirAllTest = 'AllTest'
dirParams = 'Parameters'

dirParent = 'directories'
def createDirectories():
	directories = [dirMonoRe, dirDialRe, dirMonoLabs, dirDialLabs, dirDialTrain, dirDialTest, dirMonoTrain, dirMonoTest, dirAllTrain, dirAllTest, dirParams]
	createDirectory(dirParent)
	for directory in directories:
		createDirectory(dirParent + '/' + directory)
	return 0

def unzipAll(source, target):
	for subdir, dirs, files in os.walk(source):
		for file in files:
			ext = getExtension(file)
			if ext == 'zip':
				print ("Extracting '%s'." % (file))
				zipped = zipfile.ZipFile(source+file)
				all_exists = True
				for name in zipped.namelist():
					if not op.isfile(target+name):
						all_exists = False
				if all_exists == False:
					zipped.extractall(target)
				else:
					print ("%sAll files were already unzipped in '%s'%s" % (bcolors.OKBLUE, file, bcolors.ENDC))

def resampleAll(source, target, program, rate=16000):
	print ("%sResampling '%s' into '%s' at '%s' Hz.%s" % (bcolors.BOLD, source, target, str(rate), bcolors.ENDC))
	call(["bash", program, '-s', str(rate), '-r', source, '-w', target])

def createMonoLabels(monoSheet, target):
	worksheets = [loadWorksheet(monoSheet)]
	path = [target]
	parseSpreadsheet.createLabels(worksheets, path)	

def createDialLabels(dialSheet, wavs, target):
	createDialogueLabels.createLabels(dialSheet, wavs, target)

def alreadyCreatedLabels(wavs, labs):
	for (subdir, dir, files) in os.walk(wavs):
		for file in files:
			ext = getExtension(file)
			if (ext == 'wav'):
				temp = removeExtension(file)
				if (not op.isfile(labs+temp+'.lab')):
					return False
	return True

"""
createAlot refer to creating the dictionary, .yaml file and the mapping.
"""
def createAlot(paths, target):
	print ("Create dictionary, mapping and phones list.")
	if not extensionCheck(target, 'dict'):
		worksheets = []
		for path in paths:
			if op.isfile(path):
				worksheets.append(loadWorksheet(path))
			else:
				print ("%sCould not find '%s'%s" % (bcolors.FAIL, path, bcolors.ENDC))
		parseSpreadsheet.createDictionary(worksheets, target, True)
	
		print ("%sDictionary, mapping and phones list created.%s" % (bcolors.OKGREEN, bcolors.ENDC))
	else:
		print ("%sAlready exists dictionary file in '%s'%s" % (bcolors.OKBLUE, target, bcolors.ENDC))
	print ("Creating '%s' file." % (target+'DK.yaml'))
	mapCharacters = []
	with open(target+'phonesFromMap1.txt') as f:
		for line in f.readlines():
			mapCharacters.append(line.split()[0])
	yaml_string = createYaml(mapCharacters)	
	if (not op.isfile(target+'DK.yaml')):
		createFile(target+'DK', '.yaml', [yaml_string], True)
		print ("%sCreated '%s'.%s" % (bcolors.OKGREEN, target+'DK.yaml', bcolors.ENDC))
	else:
		print ("%s'%s' already exist.%s" % (bcolors.OKBLUE, target+'DK.yaml', bcolors.ENDC))

"""
Remove the contents of a directory.
"""
def emptyDirectory(directory):
	for the_file in os.listdir(directory):
		file_path = os.path.join(directory, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutil.rmtree(file_path)
		except (Exception, e):
			print (e)

def makeArgparser():
	argparser = ArgumentParser(description='Setup for training then train.')
	argparser.add_argument('-a', '--a', help='Path to the folder containing the prosodylab-aligner.')
	argparser.add_argument('-d', '--d', help='Path to the DanPass corpus.')
	argparser.add_argument('-p', '--p', type=int, help='Training set size in percent. Eg. 60 is 60 percent training set size.')

	argparser.add_argument('-s', '--s', type=int, help='Resample rate in Hz for the files. Excluding the argument, rate will be 16000 Hz.')

	return argparser

def main(aligner_path, corpus_path, training_size, sample_rate):
	bcolors.init()
	rate = 16000
	if sample_rate is not None:
		rate = int(sample_rate)

#	aligner_path = args.a
#	corpus_path = args.d
#	training_size = args.p
	# Path should lead to a folder. So we want path to end with '/'.
	if aligner_path[len(aligner_path) - 1] != '/':
		aligner_path = aligner_path + '/'
	if corpus_path[len(corpus_path) - 1] != '/':
		corpus_path = corpus_path + '/'

	monologues_exists = op.isfile(corpus_path + 'monologues.xlsx')
	aligner_exists = op.isfile(aligner_path + 'aligner/aligner.py')
	if monologues_exists != True:
		print ("%sCould not find monologues.xlsx in '%s'\nStopping...%s" % (bcolors.WARNING, corpus_path, bcolors.ENDC))
		return 0
	if aligner_exists != True:
		print ("%sCould not find /aligner/aligner.py in '%s'\nStopping...%s" % (bcolors.WARNING, aligner_path, bcolors.ENDC))
		return 0
	
	print ("Checking if needed directories exist.")
	createDirectories()	
	
	monologues = corpus_path + 'monologues/'
	dialogues = corpus_path + 'dialogues/'
	temp = 'temporary'
	
	print ("Checking if needed temporary directories exist.")
	createDirectory(temp)
	createDirectory(temp+'/monologues/')
	createDirectory(temp+'/dialogues/')

	print ("Unzip .wav files.")
	unzipAll(monologues, temp+'/monologues/')
	unzipAll(dialogues, temp+'/dialogues/')

	alreadySampledMono = check_same(temp+'/monologues/', dirParent+'/'+dirMonoRe)
	alreadySampledDial = check_same(temp+'/dialogues/', dirParent+'/'+dirDialRe)
	if not alreadySampledMono:
		resampleAll(temp+'/monologues/', dirParent + '/' + dirMonoRe, aligner_path + 'resample.sh', rate)
	else:
		print ("%s'%s' appears already resampled.%s" % (bcolors.OKBLUE, dirParent+'/'+dirMonoRe, bcolors.ENDC))
	if not alreadySampledDial:
		resampleAll(temp+'/dialogues/', dirParent + '/' + dirDialRe, aligner_path + 'resample.sh', rate)
	else:
		print ("%s'%s' appears already resampled.%s" % (bcolors.OKBLUE, dirParent+'/'+dirDialRe, bcolors.ENDC))

	# Create .lab files.
	alreadyCreatedMonoLabs = alreadyCreatedLabels(dirParent+'/'+dirMonoRe, dirParent+'/'+dirMonoLabs+'/')
	alreadyCreatedDialLabs = alreadyCreatedLabels(dirParent+'/'+dirDialRe, dirParent+'/'+dirDialLabs+'/')
	print ("Creating monologue .lab files.")	
	if alreadyCreatedMonoLabs == False:
		createMonoLabels(corpus_path + 'monologues.xlsx', dirParent+'/'+dirMonoLabs)
		print ("%sCreated monologue labels.%s" % (bcolors.OKGREEN, bcolors.ENDC))
	else:
		print ("%sMonologue labels already exist.%s" % (bcolors.OKBLUE, bcolors.ENDC))
	
	print ("Creating dialogue .lab files.")
	if alreadyCreatedDialLabs == False:
		createDialLabels(corpus_path + 'dialogues.xlsx', dirParent+'/'+dirDialRe+'/', dirParent+'/'+dirDialLabs+'/')
		print ("%sCreated dialogue labels.%s" % (bcolors.OKGREEN, bcolors.ENDC))
	else:
		print ("%sDialogue labels already exist.%s" % (bcolors.OKBLUE, bcolors.ENDC))

	createAlot([corpus_path+'monologues.xlsx', corpus_path+'dialogues.xlsx'], dirParent+'/'+dirParams+'/')	

	# Should be ready for splitting data for training now.
	# Then afterwards we should train.
	# Maybe both do training on monologues alone, dialogues alone and then on everything together. Then we can see if it crashes somewhere. Maybe it is at least able to do monologues.

	monoWavs = getFiles(dirParent+'/'+dirMonoRe, 'wav')
	dialWavs = getFiles(dirParent+'/'+dirDialRe, 'wav')
	monoLabs = getFiles(dirParent+'/'+dirMonoLabs, 'lab')
	dialLabs = getFiles(dirParent+'/'+dirDialLabs, 'lab')

	assert len(monoWavs) == len(monoLabs)
	assert len(dialWavs) == len(dialLabs)

	monoTrainSize = int((training_size / 100.0) * len(monoWavs))
	monoTestSize = len(monoWavs) - monoTrainSize
	dialTrainSize = int((training_size / 100.0) * len(dialWavs))
	dialTestSize = len(dialWavs) - dialTrainSize

	shuffle(monoWavs)
	shuffle(dialWavs)

	monoTrainSet = [monoWavs[i] for i in range(0, monoTrainSize)]
	monoTestSet = [monoWavs[i] for i in range(monoTrainSize, len(monoWavs))]
	dialTrainSet = [dialWavs[i] for i in range(0, dialTrainSize)]
	dialTestSet = [dialWavs[i] for i in range(dialTrainSize, len(dialWavs))]

	monoTrainDirSize = len(getFiles(dirParent+'/'+dirMonoTrain, 'wav'))
	dialTrainDirSize = len(getFiles(dirParent+'/'+dirDialTrain, 'wav'))
	allTrainDirSize = len(getFiles(dirParent+'/'+dirAllTrain, 'wav'))

	monoTestDirSize = len(getFiles(dirParent+'/'+dirMonoTest, 'wav'))
	dialTestDirSize = len(getFiles(dirParent+'/'+dirDialTest, 'wav'))
	allTestDirSize = len(getFiles(dirParent+'/'+dirAllTest, 'wav'))

	print ("Copy files to training folders.")
	if monoTrainDirSize != monoTrainSize:
		emptyDirectory(dirParent+'/'+dirMonoTrain)
		transferFiles(dirParent+'/'+dirMonoRe, dirParent+'/'+dirMonoTrain, monoTrainSet, 'wav')
		transferFiles(dirParent+'/'+dirMonoLabs, dirParent+'/'+dirMonoTrain, monoTrainSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for training.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirMonoTrain), bcolors.ENDC))
		
	if dialTrainSize != dialTrainDirSize:
		emptyDirectory(dirParent+'/'+dirDialTrain)
		transferFiles(dirParent+'/'+dirDialRe, dirParent+'/'+dirDialTrain, dialTrainSet, 'wav')
		transferFiles(dirParent+'/'+dirDialLabs, dirParent+'/'+dirDialTrain, dialTrainSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for training.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirDialTrain), bcolors.ENDC))

	if monoTrainSize + dialTrainSize != allTrainDirSize:
		emptyDirectory(dirParent+'/'+dirAllTrain)
		transferFiles(dirParent+'/'+dirMonoRe, dirParent+'/'+dirAllTrain, monoTrainSet, 'wav')
		transferFiles(dirParent+'/'+dirMonoLabs, dirParent+'/'+dirAllTrain, monoTrainSet, 'lab')
		transferFiles(dirParent+'/'+dirDialRe, dirParent+'/'+dirAllTrain, dialTrainSet, 'wav')
		transferFiles(dirParent+'/'+dirDialLabs, dirParent+'/'+dirAllTrain, dialTrainSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for training.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirAllTrain), bcolors.ENDC))

	print ("Copy files to test folders.")
	if monoTestSize != monoTestDirSize: 
		emptyDirectory(dirParent+'/'+dirMonoTest)
		transferFiles(dirParent+'/'+dirMonoRe, dirParent+'/'+dirMonoTest, monoTestSet, 'wav')
		transferFiles(dirParent+'/'+dirMonoLabs, dirParent+'/'+dirMonoTest, monoTestSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for testing.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirMonoTest), bcolors.ENDC))
	
	if dialTestSize != dialTestDirSize:
		emptyDirectory(dirParent+'/'+dirDialTest)
		transferFiles(dirParent+'/'+dirDialRe, dirParent+'/'+dirDialTest, dialTestSet, 'wav')
		transferFiles(dirParent+'/'+dirDialLabs, dirParent+'/'+dirDialTest, dialTestSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for testing.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirDialTest), bcolors.ENDC))

	if monoTestSize + dialTestSize != allTestDirSize:
		emptyDirectory(dirParent+'/'+dirAllTest)
		transferFiles(dirParent+'/'+dirMonoRe, dirParent+'/'+dirAllTest, monoTestSet, 'wav')
		transferFiles(dirParent+'/'+dirMonoLabs, dirParent+'/'+dirAllTest, monoTestSet, 'lab')
		transferFiles(dirParent+'/'+dirDialRe, dirParent+'/'+dirAllTest, dialTestSet, 'wav')
		transferFiles(dirParent+'/'+dirDialLabs, dirParent+'/'+dirAllTest, dialTestSet, 'lab')
	else:
		print ("%s'%s' seems to already contain the right amount of files for testing.%s" % (bcolors.OKBLUE, (dirParent+'/'+dirAllTest), bcolors.ENDC))


	print ("%sReady for training.%s" % (bcolors.OKGREEN, bcolors.ENDC))

if __name__ == "__main__":
	argparser = makeArgparser()
	args = argparser.parse_args()
	main(args.a, args.d, args.p, args.s)
