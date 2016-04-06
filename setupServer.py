from argparse import ArgumentParser
import os
import platform
import serverHelpers.getPip
from serverHelpers.versions import Ubuntu
from subprocess import Popen, PIPE
import wget
import zipfile

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def getExtension(path):
	if '.' not in path:
		return None
	return path.rsplit(".", 1)[1]

def runProcess(arguments=[], cwd="."):
	stdout, stderr = "", ""
	try:
		p = Popen(arguments, stdout=PIPE, stderr=PIPE, cwd=cwd)
		stdout, stderr = p.communicate()
		print ("%sRan process with arguments '%s' successfully!%s" % OKGREEN, arguments, ENDC)
	except:
		print ("%sRunning process with arguments '%s' failed.%s" % FAIL, arguments, ENDC)	
	return stdout, stderr

def unzip(filename):
	zipped = zipfile.ZipFile(filename)
	zipped.extractall()

def download(url="https://github.com/Bettedaniel/ProsodyAdapters/archive/master.zip"):
	filename = wget.download(url)
	return filename

# Make it find the packed file itself.
def unpackHTK():
	subdir, dirs, files = next(os.walk(os.pardir))
	for dir in dirs:
		if 'HTK' in dir:
			print ("%sAlready unpacked '%s'.%s" % (OKBLUE, dir, ENDC))
			return
	for file in files:
		if 'HTK' in file:
			ext = getExtension(file)
			if ext == 'gz':
				stdout, stderror = runProcess(["tar", "-xvzf", file])
				return True
			elif ext == 'tar':
				stdout, stderror = runProcess(["tar", "-xvf", file])
				return True
			else:
				print ("%sCannot unpack compressed format with extension '%s'.%s" % (FAIL, ext, ENDC))
	return False

def setup(version):
#	name = download()
#	unzip(name)
	pip3Install = ["sudo", "pip3", "install"]
	stdout, stderr = runProcess(version.update())
	stdout, stderr = runProcess(version.upgrade())
	stdout, stderr = runProcess(version.install("build-essential"))
	stdout, stderr = runProcess(version.install("g++"))
	getPip.main()
	stdout, stderr = runProcess(version.install("python3-numpy"))
	stdout, stderr = runProcess(version.install("python3-scipy"))
	stdout, stderr = runProcess(["sudo", "pip3", "install", "pyyaml"])
	stdout, stderr = runProcess(["sudo", "pip3", "install", "textgrid"])
	stdout, stderr = runProcess(["sudo", "pip3", "install", "xlrd"])
	stdout, stderr = runProcess(version.install("libc6-dev-i386"))
	stdout, stderr = runProcess(version.install("sox"))
	unpacked = unpackHTK()	
	if unpacked:
		print ("%sSuccessfully unpacked HTK.%s" % (OKGREEN, ENDC))
	else:
		print ("%sFailed unpacking HTK.%s" % (FAIL, ENDC))
	htkDir = "../htk"
	stdout, stderr = runProcess(["export", "CPPFLAGS=-UPHNALG"], cwd=htkDir)
	stdout, stderr = runProcess(["./configure", "--disable-hlmtools", "--disable-hslab"], cwd=htkDir)
	stdout, stderr = runProcess(["make", "clean"], cwd=htkDir)
	stdout, stderr = runProcess(["make", "-j4", "all"], cwd=htkDir)
	stdout, stderr = runProcess(["sudo", "make", "-j4", "install"], cwd=htkDir)
	
def detectSystem():
	print (os.name)
	print (platform.system())
	print (platform.release())

if __name__ == "__main__":
#	detectSystem()
	setup(Ubuntu())