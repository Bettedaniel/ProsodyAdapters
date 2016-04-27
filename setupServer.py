from argparse import ArgumentParser
import os
import platform
from serverHelpers.versions import Ubuntu
import shutil
from subprocess import Popen, PIPE
import urllib.request
import zipfile

"""
To be truly cross platform all the path stuff should be replaced with calls to the 'os' library (E.g. os.path.join()).
"""

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
def unpackHTK(cwd="../"):
	subdir, dirs, files = next(os.walk(os.pardir))
	for dir in dirs:
		if 'HTK' in dir:
			print ("%sAlready unpacked '%s'.%s" % (WARNING, dir, ENDC))
			return False
	for file in files:
		if 'HTK' in file:
			ext = getExtension(file)
			if ext == 'gz':
				stdout, stderror = runProcess(["tar", "-xvzf", file], cwd=cwd)
				return True
			elif ext == 'tar':
				stdout, stderror = runProcess(["tar", "-xvf", file], cwd=cwd)
				return True
			else:
				print ("%sCannot unpack compressed format with extension '%s'.%s" % (FAIL, ext, ENDC))
	return False

def getProsodylab():
	if not os.path.isfile("../master.zip"):
		unzip(download(dest="../master.zip"))

def appendToBashrc(string):
	try:
		stdout, stderr = runProcess(["echo " + string + " >> " + os.path.expanduser("~/.bashrc")], shell=True)
		stdout1, stderr1 = runProcess(["source " + os.path.expanduser("~/.bashrc")], shell=True)
		print ("%sSuccesfully added '%s' to .bashrc.%s" % (OKGREEN, string, ENDC))
	except:
		print ("%sFailed adding '%s' to .bashrc.%s" % (FAIL, string, ENDC))

def installBasics(version):
	stdout, stderr = runProcess(version.update())
	stdout, stderr = runProcess(version.upgrade())
	stdout, stderr = runProcess(version.install("build-essential"))
	stdout, stderr = runProcess(version.install("libx11-dev"))
	stdout, stderr = runProcess(version.install("g++"))

def installProsody(version):
	stdout, stderr = runProcess(version.install("python3-numpy"))
	stdout, stderr = runProcess(version.install("python3-scipy"))
	stdout, stderr = runProcess(version.install("python3-pip"))
	stdout, stderr = runProcess(["sudo", "pip3", "install", "pyyaml"])
	stdout, stderr = runProcess(["sudo", "pip3", "install", "textgrid"])
	stdout, stderr = runProcess(["sudo", "pip3", "install", "xlrd"])
	stdout, stderr = runProcess(version.install("sox"))

def setupBetaHTK(version):
	installBasics(version)
	installProsody(version)
	unpacked = unpackHTK("../")	
	if unpacked:
		print ("%sSuccessfully unpacked HTK.%s" % (OKGREEN, ENDC))
	else:
		print ("%sFailed unpacking HTK.%s" % (FAIL, ENDC))
	htkDir = "../htk/"
	stdout, stderr = runProcess(["make", "-f", "MakefileCPU", "all"], cwd=htkDir+"HTKLib/")
	stdout, stderr = runProcess(["make", "-f", "MakefileCPU", "all"], cwd=htkDir+"HTKTools/")
	stdout, stderr = runProcess(["make", "-f", "MakefileCPU", "install"], cwd=htkDir+"HTKTools/")
	appendToBashrc("export PATH=$PATH:/home/ubuntu/htk/bin.cpu/")
	print ("%s%sChanged made to bashrc. In order for them to take effect please reconnect to the server.%s" % (BOLD, WARNING, ENDC))
	print ("%s%sAs an alternative to reconnecting run:\nsource ~/.bashrc%s" % (BOLD, WARNING, ENDC))

def detectSystem():
	print (os.name)
	print (platform.system())
	print (platform.release())

if __name__ == "__main__":
#	detectSystem()
	setupBetaHTK(Ubuntu())
#	getProsodylab()
