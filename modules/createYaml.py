
part1 = "# for human reading only\nauthors: Kyle Gorman\nlanguage: Danish\ncitation: \"K. Gorman, J. Howell, and M. Wagner. 2011. Prosodylab-Aligner: A tool for forced alignment of laboratory speech. Canadian Acoustics, 39(3), 192-193.\"\nURL: http://prosodylab.org/tools/aligner/\n\n# basic features\nsamplerate: 16000 # in Hz\nphoneset: "
part2 = "\n# specs for feature extractor; change at your own risk\nHCopy:\n    SOURCEKIND: WAVEFORM\n    SOURCEFORMAT: WAVE\n    TARGETRATE: 100000.0\n    TARGETKIND: MFCC_D_A_0\n    WINDOWSIZE: 250000.0\n    PREEMCOEF: 0.97\n    USEHAMMING: T\n    ENORMALIZE: T\n    CEPLIFTER: 22\n    NUMCHANS: 20\n    NUMCEPS: 12\n\n# pruning parameters, to use globally; change at your own risk\npruning: [250, 100, 5000]\n\n# specs for flat start; change at your own risk\nHCompV:\n    F: .01\n\n# specs for estimation; change at your own risk\nHERest:\n    TARGETRATE: 100000.0\n    TARGETKIND: MFCC_D_A_0\n    WINDOWSIZE: 250000.0\n    PREEMCOEF: 0.97\n    USEHAMMING: T\n    ENORMALIZE: T\n    CEPLIFTER: 22\n    NUMCHANS: 20\n    NUMCEPS: 12\n\n# specs for the decoder; change at your own risk\nHVite:\n    SFAC: 5"

def createYaml(phones):
	string = "["
	for i in range(len(phones)):
		if i == 0:
			string = string + phones[i]
		else:
			string = string + ', ' + phones[i]
	string = string + "]"

	return part1 + string + part2	
