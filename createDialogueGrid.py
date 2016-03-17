from argparse import ArgumentParser
from modules.createDialogueLabels import getData, getTeams, createFileName
from modules.Helpers import loadWorksheet, createFile
from modules.filesUtility import createDirectory
import modules.bcolors as bcolors

def getString(words):
	string = words[0]
	for i in range(1, len(words)):
		string = string + " " + words[i]	
	return string

def createGrid(directory, spreadsheet, target):
	bcolors.init()
	createDirectory(target)
	data = getData(loadWorksheet(spreadsheet))
	teams = getTeams(directory)
	
	gridData = dict()
	for team in teams:
		mono1 = (team[0], team[2])
		mono2 = (team[1], team[2])
		both = (len(data[mono1]) > 0 and len(data[mono2]) > 0)
		if both:
			merge = [quad+(team[0],) for quad in data[mono1]]
			for quad in data[mono2]:
				merge.append(quad+(team[1],))	
			gridData.setdefault(team, merge)
	
	TIME, DURATION, WORDS, SPEAKER = 0, 1, 2, 4
	for team in teams:
		sortedList = sorted(gridData[team], key=lambda tup: (tup[TIME], tup[DURATION]))
		i = 0
		file_content = "Utterance:\tname:\tmap:\tstart:\tend:\t\n"
		while i < len(sortedList):
			speaker = sortedList[i][SPEAKER]
			utterance = ""
			start = sortedList[i][TIME]
			end = -1
			while (i < len(sortedList) and speaker == sortedList[i][SPEAKER]):
				utterance = utterance + getString(sortedList[i][WORDS]) + " "
				end = sortedList[i][TIME]+sortedList[i][DURATION]
				i += 1
			file_content = file_content + utterance + "\t" + str(speaker) + "\t" + str(team[2]) + "\t" + str(start) + "\t" + str(end) + "\n"
		createFile(target+createFileName(team), '.txt', [file_content], True)
	return True

def main():
	bcolors.init()
	argparser = ArgumentParser(description="Create the dialogues grid.")
	argparser.add_argument('-d', '--dialogues', help='Path to folder with dialogue .wav files.')
	argparser.add_argument('-c', '--corpus', help='Path to the danpass corpus.')

	args = argparser.parse_args()
	if not args.dialogues is None and not args.corpus is None:
		finished = createGrid(args.dialogues, args.corpus+'/dialogues.xlsx', './gridFiles/')
		if (finished):
			print ("%sFinished.%s" % (bcolors.OKGREEN, bcolors.ENDC))
		return
	print ("%sArgument(s) missing.%s" % (bcolors.WARNING, bcolors.ENDC))
	

if __name__ == "__main__":
	main()
