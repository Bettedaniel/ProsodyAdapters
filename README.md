# ProsodyAdapters
## Description
Prodylab-Alignment adapters and other parsers

Adapters to adapt the danpass corpus data to fit with the prosodylab-alignment software.

## Language
Everything is implemented using python version 3.4.3.

## Running the program(s) 
In order to set up the project call:
python3 setupTraining.py -a "path to aligner" -d "path to danpass corpus" -p "training set size in percent"
Example:
python3 setupTraining.py -a Prosodylab-Aligner/ -d DanPass/ -p 60

After setting up the project, the prosodylab aligner can be used to train on the files in directories/MonoTrain/, directories/DialTrain or directories/AllTrain. Dictionary and .yaml file will be in directories/Parameters.

To evaluate performance run:
To fetch the needed data.
python3 setupEvaluation.py -f "path to danpass corpus"

To fix .TextGrid files in a selected tier. Fixes danish characters and fixes some white space differences. (Creates new fixed files, does not overwrite old)
python3 setupEvaluation.py -d "Path to directory with TextGrid files" "tier name"

For two directories compare performance between all .TextGrid files with the same names. Always compares the first tier. If run on cleaned .TextGrid directory then there will only be one tier.
python3 setupEvaluation.py -c  "path to directory one" "path to directory two"

The file createDialogueGrid.py will create a file for each dialogues file where every utterance (uninterrupted sequence of word by a speaker) is transcribed with timings and who uttered it.
To run it:
python3 createDialogueGrid.py -d "Path to folder with dialogue files" -c "path to danpass corpus"
