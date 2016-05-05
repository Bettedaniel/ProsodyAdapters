from argparse import ArgumentParser
import json
import modules.bcolors as bcolors
import boto3
import os.path as op

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
	instances = response.get('Instances')
	for instance in instances:
		instanceIds.append(instance.get('InstanceId'))
	return instanceIds

def doWork(access, secret, key):
	ec2 = boto3.client('ec2', aws_access_key_id=access, aws_secret_access_key=secret, region_name='eu-central-1')
	response = ec2.run_instances(ImageId='ami-87564feb', InstanceType='t2.micro', MinCount=1, MaxCount=1, KeyName=key)
	instanceIds = getInstanceIds(response)
	print (instanceIds)
	print ("@@@@@@@@@@@@@@@@@")
	response = ec2.terminate_instances(InstanceIds=instanceIds)
	print (response)

def main(path, key):
	print ("Called main with %s" % (path))
	if (not op.isfile(path)):
		print ("%s'%s' is not a file.%s" % (bcolors.FAIL, path, bcolors.ENDC))
		return
	access, secret = readCredentials(path)	
	doWork(access, secret, key)

	return

if __name__ == "__main__":
	argparser = ArgumentParser(description="lorem ipsum aws.")

	argparser.add_argument('-c', '--credentials', type=str, help="Path to AWS AMI credentials file.")
	argparser.add_argument('-k', '--key', type=str, help="Name of key.")

	args = argparser.parse_args()
	main(args.credentials, args.key)
