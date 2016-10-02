from argparse import ArgumentParser
import modules.bcolors as bcolors
from modules.filesUtility import createDirectory
import os
from random import shuffle
import shutil

crossValidationTraining = "directories/crossValidationTrain"
crossValidationTest = "directories/crossValidationTest"

def getExtension(file):
	if (not "." in file):
		return None
	return file.rsplit(".", 1)[1]

def getFilename(file):
	if (not "." in file):
		return file
	return file.rsplit(".", 1)[0]

def createDirectoryAndCopyData(data, directory):
	createDirectory(directory)
	for file in data:
		shutil.copy(file, directory)

def addCorrespondingLabFiles(data):
	result = []
	for file in data:
		fileName = getFilename(file)
		result.append(file)
		result.append(fileName+'.lab')
	return result
	
def splitWavsAndLabs(directory):
	wavs = []
	labs = []
	for subdir, dirs, files in os.walk(directory):
		for file in files:
			ext = getExtension(file)
			if ext == "wav":
				wavs.append(os.path.join(directory, file))
			elif ext == "lab":
				labs.append(os.path.join(directory, file))
			else:
				print ("%sInvalid file type '%s'.%s" % (bcolors.WARNING, ext, bcolors.ENDC))
	return wavs, labs

def main():
	bcolors.init()
	argparser = ArgumentParser(description='Do k-fold cross validation.')
	argparser.add_argument('-k', '--k', help='The k in k-fold cross validation. Defaults to 10.', default=10)
	argparser.add_argument('-m', '--m', help='Path to the folder with the wav and lab monologues.')
	argparser.add_argument('-d', '--d', help='Path to the folder with the wav and lab dialogues.')
	
	args = argparser.parse_args()
	k = args.k
	
	# Only use the labs to check how many there are.
	# If number of wavs != number of labs, then something is wrong.
	entireSetOfWavs, entireSetOfLabs = splitWavsAndLabs(args.m)
	tempWavs, tempLabs = splitWavsAndLabs(args.d)
	entireSetOfWavs += tempWavs
	entireSetOfLabs += tempLabs

	print ("%sFound %s wav files%s" % (bcolors.OKGREEN, len(entireSetOfWavs), bcolors.ENDC))
	print ("%sFound %s lab files%s" % (bcolors.OKGREEN, len(entireSetOfLabs), bcolors.ENDC))


	sampleSize = int(len(entireSetOfWavs) / k)

	shuffle(entireSetOfWavs)

	samples = [entireSetOfWavs[x:x+sampleSize] for x in range(0, len(entireSetOfWavs), sampleSize)]
	
	for i in range(0, len(samples)):
		iteration = ("round%s" % (i+1))
		createDirectoryAndCopyData(addCorrespondingLabFiles(samples[i]), os.path.join(crossValidationTest, iteration))
		rest = []
		for j in range(0, len(samples)):
			if i == j:
				continue
			rest.extend(samples[j])
		createDirectoryAndCopyData(addCorrespondingLabFiles(rest), os.path.join(crossValidationTraining, iteration))

	# Every part of the k-fold validation gets their own folder. Just in case data wants to be kept. Introduces a large degree of replication of data. Might take up a lot of harddisk space.
	# Now train and evaluate each iteration and average the score...

if __name__ == "__main__":
	main()
