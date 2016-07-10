import os.path as op
import os
import shutil
from subprocess import call
import zipfile
import modules.bcolors as bcolors

def createDirectory(directory):
	if not op.exists(directory):
		print ("%s'%s' does not exist.%s" % (bcolors.FAIL, directory, bcolors.ENDC))
		os.makedirs(directory)
		print ("\t%sCreated '%s'.%s" % (bcolors.OKGREEN, directory, bcolors.ENDC))
	else:
		print ("%s'%s' already exists.%s" % (bcolors.OKBLUE, directory, bcolors.ENDC))

def getExtension(f):
	if not '.' in f:
		return ""
	return f.rsplit('.', 1)[1]

def removeExtension(f):
	if not '.' in f:
		return f
	return f.rsplit('.', 1)[0]

def removeFolder(target):
	print ("Removing '%s'." % (target))
	if op.exists(target):
		call(['rm', '-rf', target])
	else:
		print ("'%s' does not exist." % (target))


def removePath(f):
	if not "/" in f:
		return f
	return f.rsplit('/', 1)[1]

"""
Check if 'directory' contains a file with the extension 'extension'.
"""
def extensionCheck(directory, extension):
	for subdir, dir, files in os.walk(directory):
		for file in files:
			ext = getExtension(file)
			if ext == extension:
				return True
	return False

"""
Get files with extension 'extension' in 'directory'.
"""
def getFiles(directory, extension):
	extFiles = []
	for subdir, dir, files in os.walk(directory):
		for file in files:
			ext = getExtension(file)
			if (extension == ext):
				extFiles.append(file)
	return extFiles

"""
Transfer files matching the file names in fileNames, with the extension ''extension'.
"""
def transferFiles(source, dest, fileNames, extension):
	fileNames = [removeExtension(file) for file in fileNames]
	for subdir, dir, files in os.walk(source):
		for file in files:
			file_ = removeExtension(file)
			if file_ in fileNames:
				shutil.copy(source+'/'+file_+'.'+extension, dest)
	print ("%sCopied files from '%s' to '%s'.%s" % (bcolors.OKGREEN, source, dest, bcolors.ENDC))

"""
Check if source and target contains files of the same names.
"""
def check_same(source, target):
	same = True
	for subdir, dir, files in os.walk(source):
		for file in files:
			ext = getExtension(file)
			if ext == 'wav':
				if not op.isfile(target+'/'+file):
					same = False
	return same

def endOnSlash(directory):
	if directory[len(directory) - 1] == '/':
		return directory
	return directory + '/'
