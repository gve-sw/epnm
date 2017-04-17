import csv
import base64
import pandas as pd
from epnm import EPNM
from device import Device, ASR, NCS

host = "198.18.134.7"
username = "user"
password = "Tester123"
encoded_auth = base64.b64encode(username + ":" + password)

manager = EPNM(host, encoded_auth)

dev_addr_df = pd.read_csv('dev_address_test_NoASR.csv')
connections_df = pd.read_csv('connections_test_NoASR.csv')

print dev_addr_df
print (" ")

num_rows = dev_addr_df.shape[1] + 1

devices = {}

#create the device objects
for i in range(0, num_rows):
	device_name = dev_addr_df.loc[i]['Device Name']
	device_mgmt_ip = dev_addr_df.loc[i]['Mgmt']
	device_lo_ip = dev_addr_df.loc[i]['Loopback0']

	device_epnm_id = manager.getIDfromIP(device_mgmt_ip)
	print 'info.py '+str(device_epnm_id)
	soft_type = manager.getSWfromID(device_epnm_id)

	if soft_type == 'IOS-XE':
		devices[device_name] = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)

print devices

#add interfaces to the device objects
cols, rows = connections_df.shape

def makeInts(conn_df, dev_dict, start):
	if start == 'A':
		idx = 0
		inc = 1
	else: 
		idx = 5
		inc = -1

	cur_dev = devices[connections_df.loc[j][idx]]
	idx += inc
	new_int_name = connections_df.loc[j][idx]
	idx += inc
	new_int_addr_mask = connections_df.loc[j][idx]
	new_int_addr, new_int_mask = new_int_addr_mask.split('/')

	cur_dev.addInt(new_int_name, new_int_addr, new_int_mask)
	return


for j in range(0, rows+1):
	makeInts(connections_df, devices, 'A')
	makeInts(connections_df, devices, 'Z')

print devices