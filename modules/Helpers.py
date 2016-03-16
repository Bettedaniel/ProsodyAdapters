import xlrd
import os.path as op
import os

def loadWorksheet(location, sheet=0):
	workbook = xlrd.open_workbook(location)
	return workbook.sheet_by_index(sheet)

def createFile(name, file_type, data, override=False):
	if (override):
		with open(name+file_type, 'w') as target:
			for d in data:
				target.write(d+'\n')
	else:
		version = 1	
		while (op.isfile(name+str(version)+file_type)):
			version = version + 1
		with open(name+str(version)+file_type, 'w') as target:
			for d in data:
				target.write(d + '\n')

def extractWord(s):
	s0 = s.split()
	result = []
	for elem in s0:
		result.append(elem.split('/')[0])
	return result

def findColumn(sheet, column_name):
	for column in range(sheet.ncols):
		if (sheet.cell(0, column).value.lower() == column_name.lower()):
			return column

# Requires file identifiers to be in column 0.
def extractData(sheets):
	transcriptions = dict()
	words = []
	phonetics = dict()
	for sheet in sheets:
		pos_column = findColumn(sheet, 'PoS')
		lydskrift_column = findColumn(sheet, 'idealiseret lydskrift')	
		for row in range(sheet.nrows):
			if (row == 0):
				continue
			fileName = sheet.cell(row, 0).value
			word = extractWord(sheet.cell(row, pos_column).value)
			phones = (sheet.cell(row, lydskrift_column).value).split()
			if word and phones:
				transcriptions.setdefault(fileName, []).append(word)
				phonetics.setdefault(fileName, []).append((word, phones))
				for w in word:
					if w not in words:
						words.append(w)
	return words, transcriptions, phonetics

def createDictionary(phonetics, path, doMap=False):
	dictionary = []
	usedWords = []
	phones = []
	for key in phonetics:
		for elem in phonetics[key]:
			# If assertion does not hold, then we have fewer pronounciations than words. We can not handle the other case since this requires special casing. So we just skip.
		#	assert (len(elem[0]) <= len(elem[1])), print("%s vs. %s" % (elem[0], elem[1]))
			if len(elem[0]) > len(elem[1]):
				continue
			for i in range(len(elem[0])):
				word = elem[0][i].upper()
				# If several pronounciations, we choose the first.
				pronounciation = (elem[1][i]).split('/')[0]
				# No duplicates.
				if word not in usedWords:
					usedWords.append(word)
					dictionary.append((word, pronounciation))
	dictionary.sort(key=lambda tup: tup[0])
	phones = []
	for tup in dictionary:
		for phone in tup[1]:
			if phone not in phones:
				phones.append(phone)
	dictData = []
	name = ''
	if doMap:
		leftSide, rightSide, usedMappings = createMapping(phones)
		mappingData = []
		mappings = []
		assert(len(leftSide) == len(rightSide)), print("len(leftSide)=%s != len(rightSide)=%s" % (len(leftSide, len(rightSide))))
		for i in range(len(leftSide)):
			mappingData.append(leftSide[i]+' '+rightSide[i])
		string = "["
		for i in range(len(usedMappings)):
			mappings.append(usedMappings[i])
#			if i == 0:
#				string = string + usedMappings[i]
#			else:
#				string = string + ', ' + usedMappings[i]
#		string = string + ']'
#		mappings.append(string)
		createFile(path+'mapping', '.txt', mappingData)
		createFile(path+'phonesFromMap', '.txt', mappings)

		mp1, mp2 = getDictMaps(leftSide, rightSide)
		for tup in dictionary:
			string = str(tup[0])
			for phone in tup[1]:
				string = string + " " + mp1[phone]
			dictData.append(string)
		name = 'dictionaryDKMapped'
	else:
		string = "["
		for i in range(len(phones)):
			if i == 0:
				string = string + phones[i]
			else:
				string = string + ', ' + phones[i]
		string = string + ']'
		createFile(path+'phones', '.txt', [string])

		dictData = []
		for tup in dictionary:
			string = str(tup[0])
			for phone in tup[1]:
				string = string + " " + phone
			dictData.append(string)
		name = 'dictionaryDK'
	createFile(path+name, '.dict', dictData)


		
def getDictMaps(leftSide, rightSide):
	mp1 = dict()
	mp2 = dict()
	for i in range(len(leftSide)):
		mp1.setdefault(leftSide[i], rightSide[i])
		mp2.setdefault(rightSide[i], leftSide[i])
	return mp1, mp2

def createMany(amount, letters, numbers):
	mappings = []
	for letter in letters:
		mappings.append(letter)
	created = len(letters)
	switch = True
	while created < amount:
		temp = list(mappings)
		for mapping in temp:
			if switch:
				for number in numbers:
					assert mapping+number not in mappings, print(mappings)
					mappings.append(mapping+number)
					created = created + 1
			else:
				for letter in letters:
					assert mapping+letter not in mappings, print(mappings)
					mappings.append(mapping+letter)
					created = created + 1
		switch = not switch
	return mappings
				
def createMapping(phones):
	letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
	numbers = ['0', '1', '2', '3', '4', '5', '6']
	leftSide = [] # Holds the phones.
	rightSide = [] # Holds the mappings.
	available = createMany(len(phones)+1, letters, numbers)
	index = 0
	for phone in phones:
		if (phone not in leftSide):
			leftSide.append(phone)
			rightSide.append(available[index])
			index = index + 1
	usedMappings = available[0:index]
	return leftSide, rightSide, usedMappings

#Files contains if mono or dial
def makeMappingFromFileToPath(sheets, files):
	result = dict()
	for directory in files:
		if not op.exists(directory):
			print ("Directory %s does not exist please create manually." % (directory))
			return result
	for i in range(len(sheets)):
		sheet = sheets[i]
		path = files[i]
		for row in range(sheet.nrows):
			fileName = sheet.cell(row, 0).value
			result.setdefault(fileName, path)
	return result

def createTranscriptions(transcriptions, fileToPathMap):
	labels = []
	for key in transcriptions:
		label = ""
		i = 0
		for words in transcriptions[key]:
			for word in words:
				word = word.upper()
				if (i > 0):
					label = label + " " + word
				else:
					label = word
				i = i + 1
		labels.append((fileToPathMap[key], key, label))	
	for trip in labels:
		createFile(trip[0]+'/'+trip[1], '.lab', [trip[2]], True)
	return 0


