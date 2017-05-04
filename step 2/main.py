"""
WARNING:
This script is meant for educational purposes only.
Any use of these scripts and tools is at
our own risk. There is no guarantee that
they have been through thorough testing in a
comparable environment and we are not
responsible for any damage or data loss
incurred with their use.

INFORMATION:
If you have further questions about this API and script, please contact GVE. Here are the contact details:
   For internal Cisco employees, please contact GVE at http://go2.cisco.com/gve
   For Cisco partners, please open a case at www.cisco.com/go/ph
"""

import csv
import base64
import pandas as pd
import pprint
from epnm import EPNM
from device import Device, ASR, NCS
import getpass
from time import sleep

f = open('login.txt', 'r')
host = f.readline()
host = host.strip('\n')
username = f.readline()
f.close()

password = getpass.getpass()

encoded_auth = base64.b64encode(username + ":" + password)

#instantiate instance of EPNM to handle API calls
manager = EPNM(host, encoded_auth)

#load the device and connections info from provided CSV files
dev_addr_df = pd.read_csv('dev_address_test_NoASR.csv')
connections_df = pd.read_csv('connections_test_NoASR.csv')

#number of rows corresponds to number of devices being managed
num_rows = dev_addr_df.shape[1]
devices = {}

#create one device object per iteration
for i in range(0, num_rows):
	#get the information provided in the dev_address CSV file
	device_name = dev_addr_df.loc[i]['Device Name']
	device_mgmt_ip = dev_addr_df.loc[i]['Mgmt']
	temp = dev_addr_df.loc[i]['Loopback0']
	device_lo_ip = temp.split('/')[0]
	
	#Use the management IP address to get the corresponding device ID from EPNM
	device_epnm_id = manager.getIDfromIP(device_mgmt_ip)
	#determine the software type based on device info provided by EPNM
	soft_type = manager.getSWfromID(device_epnm_id)

	#instantiate object based on software type
	if soft_type == 'IOS-XE':
		devices[device_name] = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)

#add interfaces to the device objects
rows, cols = connections_df.shape

def makeInts(conn_df, dev_dict, start):
	'''
	function takes the connections dataframe loaded from CSV, 
	splits the frame to pull both A and Z ports
	and instantiates the interfaces on the appropriate device object
	'''

	#determine if we're handling an A or Z port
	if start == 'A':
		idx = 0
		inc = 1
	else: 
		idx = 5
		inc = -1

	#get device name from df
	new_idx = connections_df.axes[1][idx]
	cur_dev = devices[connections_df.loc[j][new_idx]]

	#get the name for the new interface
	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_name = connections_df.loc[j][new_idx]

	#get the interface address and mask then split it
	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_addr_mask = connections_df.loc[j][new_idx]

	new_list = new_int_addr_mask.split('/')
	new_int_addr, new_int_mask = new_list[0], new_list[1]

	#create the new interface object on the device object specified
	cur_dev.addInt(new_int_name, new_int_addr, new_int_mask)
	return

#iterate over the rows in the connections table to create the interfaces
for j in range(0, rows):
	makeInts(connections_df, devices, 'A')
	makeInts(connections_df, devices, 'Z')

file = open("output.txt", "w")
file.close()
#deploy the templates on the devices
print "About to call templateDeploymentMaster"
manager.templateDeploymentMaster(devices)
print "Returned from templateDeploymentMaster"
sleep(10)

manager.verifyJobResult()