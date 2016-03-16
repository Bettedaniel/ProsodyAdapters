"""
We remove all the pauses, but the textgrid module adds pauses to make sure that the .TextGrid files fills out, all these pauses are the empty string ones.
"""
from argparse import ArgumentParser
from modules.Helpers import loadWorksheet, findColumn
import textgrid
from textgrid import IntervalTier
from textgrid import TextGrid
import itertools, collections
import os.path as op

VERBOSE = False

def isPause(mark=''):
	result = (not mark) or (mark == '') or (mark == '+_')
	result = result or (mark == 'sil') or (mark == 'sp')
	result = result or (mark == '=_')
	return result

def consume(iterator, n):
	collections.deque(itertools.islice(iterator, n))

def fixString(string):
	iterator = iter(range(len(string)))
	output_string = ""
	for i in iterator:
		if string[i:i+8] == '\\303\\205':
			output_string = output_string + 'å'
			consume(iterator, 7)
		elif string[i:i+8] == '\\303\\206':
			output_string = output_string + 'æ'
			consume(iterator, 7)
		elif string[i:i+8] == '\\303\\230':
			output_string = output_string + 'ø'
			consume(iterator, 7)
		elif string[i:i+8] == '\\303\\211':
			output_string = output_string + 'é'
			consume(iterator, 7)
		else:
			output_string = output_string + string[i]
	return output_string.lower()


def yankData(path):
	sheet = loadWorksheet(path)
	nameColumn = findColumn(sheet, 'filnavn')
	timeColumn = findColumn(sheet, 'tid')
	durationColumn = findColumn(sheet, 'varighed')
	posColumn = findColumn(sheet, 'PoS')
	data = []
	for row in range(1, sheet.nrows):
		name = sheet.cell(row, nameColumn).value
		time = float(sheet.cell(row, timeColumn).value)
		duration = float(sheet.cell(row, durationColumn).value)
		pos = sheet.cell(row, posColumn).value.split()
		words = []
		for part in pos:
			words.append(part.split('/')[0])
		data.append((name, time, duration, words))
	return data

def makeSentence(wordList):
	if len(wordList) == 0:
		return ""
	string = wordList[0]
	for i in range(1, len(wordList)):
		string = string + " " + wordList[i]
	return string
	
"""
Assume all names in data are the same and sorted.
Should be ensured before this is called.
"""
def createTextGrid(data, tierName = "words"):
	tier = IntervalTier(tierName)
	txtgrid = TextGrid()
	prevTime = 0
	for (name, time, dur, words) in data:
		tier.add(prevTime, prevTime+dur, makeSentence(words))
		prevTime += dur
	txtgrid.append(tier)
	return txtgrid

def createNew(textgrid, tier_name, VERBOSE=False):
	tiers = textgrid.getList(tier_name)
	tier = tiers[0]
	new_tier = IntervalTier(tier_name+'_clean') 
	new_txtgrid = TextGrid()
	if VERBOSE == True:
		print ("Old tier: %s" % tier)
	for interval in tier:
		if isPause(interval.mark) == True:
			new_tier.add(interval.minTime, interval.maxTime, '')
		else:
			new_tier.add(interval.minTime, interval.maxTime, fixString(interval.mark))
	new_txtgrid.append(new_tier)
	if VERBOSE == True:
		print ("New tier: %s" % new_tier)
	return new_txtgrid

def main():
	argparser = ArgumentParser(description="Remove pauses from a specific tier of .TextGrid files.")
	argparser.add_argument('-r', '--r', nargs=2, metavar=('PATH', 'TIER_NAME'), help='Path to .TextGrid file and name of tier.')
	argparser.add_argument('-t', '--t', nargs=1, metavar='target', help='Path to target file for cleaned textgrid.')
	argparser.add_argument('-v', '--v', dest='isVerbose', action='store_const', const=True, default=False, help='Make verbose.')
	args = argparser.parse_args()
	txtgrid = TextGrid.fromFile(args.r[0])
	clean_txtgrid = createNew(txtgrid, args.r[1], args.isVerbose)
	target = args.t[0]
	print (target)
	if (op.isfile(target)):
		clean_txtgrid.write(target)
	else:
		print ("Target file '%s' does not exist." % (target))

if __name__ == "__main__":
	main()
