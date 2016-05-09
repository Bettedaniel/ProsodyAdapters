from argparse import ArgumentParser
import json
import modules.bcolors as bcolors
import boto3
import os.path as op
from setupServer import runProcess
import sys
import time

"""
On servers boto3 will be needed.
"""
def readCredentials(path):
	with open(path, 'r') as cred:
		lines = cred.readlines()
#	cols = lines[0].split(',')
	vals = lines[1].split(',')
	return vals[1], vals[2]

def getInstanceIds(response):
	instanceIds = []
	for instance in response:
		instanceIds.append(instance.id)
	return instanceIds

"""
Had to set up an ami user on aws.amazon.com. I gave it administrator rights.

Fix security group stuff to make sure the right port is open.
"""
def doWork(access, secret, key, pem):
	ec2 = boto3.resource('ec2', 
		region_name='eu-central-1', 
		aws_access_key_id=access, 
		aws_secret_access_key=secret)
	response = ec2.create_instances(ImageId='ami-87564feb', 
									MinCount=1, 
									MaxCount=1, 
									InstanceType='t2.micro', 
									KeyName=key)
	instanceIds = getInstanceIds(response)
	running = waitForRunning(ec2, instanceIds[0])
	dns = ec2.Instance(instanceIds[0]).public_dns_name
	address = "ubuntu@"+dns
	waitForOk(ec2, instanceIds[0])
		
	upload("setupServer.py", pem, address)
	upload("serverHelpers/", pem, address)
	upload("modules/", pem, address)
	print (address)
#	ec2.instances.filter(InstanceIds=instanceIds).terminate()

def getStatus(response, statusType="InstanceStatus"):
	return response.get("InstanceStatuses")[0].get(statusType).get("Status")

def upload(path, pem, address):
	stdout, stderr = runProcess(["rsync", "-avzP", "-e", "\'ssh", "-i", "\""+pem+"\"\'", path, address+":/home/ubuntu/"])
#	if stdout is not None:
#		print ("Stdout:\n%s" % (stdout.decode("ascii")))

def waitForOk(ec2, instanceId):
	try:
		status = ""
		while (status != "ok"):
			response = ec2.meta.client.describe_instance_status(InstanceIds=[instanceId])
			status = getStatus(response)
			if status == "ok":
				print ("%sStatus: %s.%s" % (bcolors.OKGREEN, status, bcolors.ENDC))
			else:
				print ("%sStatus: %s.%s" % (bcolors.WARNING, status, bcolors.ENDC))
			time.sleep(5)
	except:
		print (sys.exc_info()[0])
		print (sys.exc_info()[1])
		print ("%sError occured while waiting for instance to reach status 'ok'.%s" % (bcolors.FAIL, bcolors.ENDC))
		return False
	return True

"""
Returns True if the instance is running, and False if an error occured.
"""
def waitForRunning(ec2, instanceId):
	try:
		state = ""
		while (state != "running"):
			time.sleep(5)
			state = ec2.Instance(instanceId).state['Name']
			if state == "running":
				print ("%sState: %s.%s" % (bcolors.OKGREEN, state, bcolors.ENDC))
			else:
				print ("%sState: %s.%s" % (bcolors.WARNING, state, bcolors.ENDC))
	except:
		print ("%sError occured while waiting for instance to reach state 'running'.%s" % (bcolors.FAIL, bcolors.ENDC))
		return False
	return True

def main(path, key, pem):
	bcolors.init()
#	print ("Called main with %s" % (path))
	if (not op.isfile(path)):
		print ("%s'%s' is not a file.%s" % (bcolors.FAIL, path, bcolors.ENDC))
		return
	access, secret = readCredentials(path)	
	doWork(access, secret, key, pem)

	return

if __name__ == "__main__":
	argparser = ArgumentParser(description="lorem ipsum aws.")

	argparser.add_argument('-c', '--credentials', type=str, help="Path to AWS AMI credentials file.")
	argparser.add_argument('-k', '--key', type=str, help="Name of key.")
	argparser.add_argument('-p', '--pem', type=str, help="Path to key file.")

	args = argparser.parse_args()
	main(args.credentials, args.key, args.pem)
