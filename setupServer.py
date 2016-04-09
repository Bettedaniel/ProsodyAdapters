from argparse import ArgumentParser
import os
import platform
from serverHelpers.versions import Ubuntu
import shutil
from subprocess import Popen, PIPE
import urllib.request
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

def runProcess(arguments=[], cwd=".", shell=False, env=None):
	stdout, stderr = "", ""
	try:
		p = Popen(arguments, stdout=PIPE, stderr=PIPE, cwd=cwd, shell=shell, env=env)
		print ("%sRan process with arguments '%s' successfully!%s" % (OKGREEN, arguments, ENDC))
		stdout, stderr = p.communicate()
	except:
		print ("%sRunning process with arguments '%s' failed.%s" % (FAIL, arguments, ENDC))
		stdout, stderr = p.communicate()
	return stdout, stderr

def findDestination(filename):
	if not "/" in filename:
		return "."
	return filename.rsplit("/", 1)[0]

def unzip(filename):
	zipped = zipfile.ZipFile(filename)
	zipped.extractall(path=findDestination(filename))

def download(url="https://github.com/prosodylab/Prosodylab-Aligner/archive/master.zip", dest="master.zip"):
	try:
		with urllib.request.urlopen(url) as response, open(dest, "wb") as out:
			shutil.copyfileobj(response, out)
		print ("%sSuccessfully downloaded '%s' into '%s'.%s" % (OKGREEN, url, dest, ENDC))
	except:
		print ("%sFailure while downloading '%s' into '%s'.%s" % (FAIL, url, dest, ENDC))
	return dest

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
				stdout, stderror = runProcess(["tar", "-xvzf", file], cwd="../")
				return True
			elif ext == 'tar':
				stdout, stderror = runProcess(["tar", "-xvf", file], cwd="../")
				return True
			else:
				print ("%sCannot unpack compressed format with extension '%s'.%s" % (FAIL, ext, ENDC))
	return False

def getProsodylab():
	if not os.path.isfile("../master.zip"):
		unzip(download(dest="../master.zip"))

def setup(version):
#	name = download()
#	unzip(name)
	pip3Install = ["sudo", "pip3", "install"]
	stdout, stderr = runProcess(version.update())
	stdout, stderr = runProcess(version.upgrade())
	stdout, stderr = runProcess(version.install("build-essential"))
	stdout, stderr = runProcess(version.install("g++"))
	stdout, stderr = runProcess(["sudo", "python3", "getPip.py"], cwd="serverHelpers/")
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
	os.environ["CPPFLAGS"] = "-UPHNALG"
	stdout, stderr = runProcess(["make", "clean"], cwd=htkDir, shell=True, env=os.environ)
	stdout, stderr = runProcess(["make", "-j4", "all"], cwd=htkDir, shell=True, env=os.environ)
	stdout, stderr = runProcess(["sudo", "make", "-j4", "install"], cwd=htkDir, shell=True, env=os.environ)

def detectSystem():
	print (os.name)
	print (platform.system())
	print (platform.release())

if __name__ == "__main__":
#	detectSystem()
	setup(Ubuntu())
	getProsodylab()
