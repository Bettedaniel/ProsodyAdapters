import argparse
from textgrid import TextGrid
import os.path as op
from modules.cleanTextgrids import createNew

def close_enough(dx, dy, close):
	return abs(dx - dy) < close

"""
Make assumption that the two TextGrids contain all the same words, in the same order. Just with different timings.
"""
def smart_evaluate(first_clean, second_clean, closeness=0.5):
	tier_names1 = first_clean.getNames()
	tier_names2 = second_clean.getNames()
	
	assert (len(tier_names1) > 0 and len(tier_names2) > 0)

	tiers1 = first_clean.getList(tier_names1[0])
	tiers2 = second_clean.getList(tier_names2[0])

	tier1 = tiers1[0]
	tier2 = tiers2[0]

	i = 0 #Index in first_clean
	j = 0 #Index in second_clean
	startCorrect, startIncorrect = 0, 0
	endCorrect, endIncorrect = 0, 0
	durCorrect, durIncorrect = 0, 0


	while (i < len(tier1) and j < len(tier2)):
		interval1 = tier1[i]
		interval2 = tier2[j]

		s1 = interval1.mark
		s2 = interval2.mark

		if s1 == "":
			i += 1
			continue
		if s2 == "":
			j += 1
			continue

		start1 = interval1.minTime
		start2 = interval2.minTime

		end1 = interval1.maxTime
		end2 = interval2.maxTime

		while s1.lower() != s2.lower():
			if len(s1) < len(s2):
				i += 1
				while (tier1[i].mark == ""):
					i += 1
				s1 = s1 + " " + tier1[i].mark
				end1 = tier1[i].maxTime
			elif len(s1) > len(s2):
				j += 1
				while (tier2[j].mark == ""):
					j += 1
				s2 = s2 + " " + tier2[j].mark
				end2 = tier2[j].maxTime
			else:
				assert (s1.lower() == s2.lower())
		print ("%s\t%.2f\t%.2f\t%.2f\n%s\t%.2f\t%.2f\t%.2f" % (s1.lower(), start1, end1, (end1-start1), s2.lower(), start2, end2, (end2-start2)))
		if close_enough(end1, end2, closeness):
			 endCorrect += 1
		else:
			endIncorrect += 1
		if close_enough(start1, start2, closeness):
			startCorrect += 1
		else:
			startIncorrect += 1
		if close_enough(end1-start1, end2-start2, closeness):
			durCorrect += 1
		else:
			durIncorrect += 1
		i += 1
		j += 1

#	return startCorrect / float(startCorrect + startIncorrect)
	return endCorrect / float(endCorrect + endIncorrect)
#	return durCorrect / float(durCorrect + durIncorrect)



"""
Skips every element not present in the dictionary.
This is to give a crude estimate of performance for the words we do detect.
This ONLY considers words pronounced present in the dictionary.
"""
def evaluate_skip_some(first_clean, second_clean, dictionary, closeness=0.5):
	tier_names1 = first_clean.getNames()
	tier_names2 = second_clean.getNames()
	
	tiers1 = first_clean.getList(tier_names1[0])
	tiers2 = second_clean.getList(tier_names2[0])
	
	tier1 = tiers1[0]
	tier2 = tiers2[0]
	
	i = 0
	j = 0

	equal = 0
	inequal = 0

	while ((i < len(tier1) and j < len(tier2))):
		interval1 = tier1[i]
		interval2 = tier2[j]
		if interval1.mark not in dictionary:
			i = i + 1
		if interval2.mark not in dictionary:
			j = j + 1
		if interval1.mark.lower() == interval2.mark.lower():
			if (close_enough(interval1.maxTime, interval2.maxTime, closeness)):
				equal = equal + 1
			else:
				inequal = inequal + 1
			i = i + 1
			j = j + 1
		
	value = equal / float(equal + inequal)

	return value

def getDictionary(path):
	dictionary = set()
	with open(path) as read:
		for line in read.readlines():
			elements = line.split()
			dictionary.add(elements[0])
	return dictionary

def main():
	argparser = argparse.ArgumentParser(description='Assign a score based on similarity of two .TextGrid files.')
	argparser.add_argument('-first', '--first', nargs=2, metavar=('PATH', 'TIER_NAME'), help='Path to the first .TextGrid file.')
	argparser.add_argument('-second', '--second', nargs=2, metavar=('PATH', 'TIER_NAME'), help='Path to the second .TextGrid file.')
	argparser.add_argument('-d', '--d', nargs=1, help='Path to dictionary file.')
	argparser.add_argument('-close', '--close', nargs='?', default=500, const=500, help='Define how close, close is in milliseconds. Used for equality test.')

	args = argparser.parse_args()

	if not op.isfile(args.first[0]):
		print ("First file '%s' does not exist." % args.first[0])
	if not op.isfile(args.second[0]):
		print ("Second file '%s' does not exist." % args.second[0])
	if not op.isfile(args.d[0]):
		print ("Dictionary file '%s' does not exist." % args.d[0])

	first = TextGrid.fromFile(args.first[0])
	second = TextGrid.fromFile(args.second[0])

	first_clean = createNew(first, args.first[1])
	second_clean = createNew(second, args.second[1])

	dictionary = getDictionary(args.d[0])
	try:
		closeness = int(args.close) / float(1000)
	except:
		print ("(-close or --close) argument should be integer.\nDefaulting to 500.")
		closeness = 0.5

#	result_skips = evaluate_skip_some(first_clean, second_clean, dictionary, closeness)
	result_smart = smart_evaluate(first_clean, second_clean, closeness)
	print ("Evaluation with skips:\n\tR=%.4f " % result_skips)	

	return 0

if __name__ == "__main__":
	main()
