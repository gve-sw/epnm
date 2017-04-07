import csv
import pandas as pd
from epnm.py import EPNM
from device.py import Device, ASR, NCS

host = "198.18.134.7"
username = "user"
password = "Tester123"
encoded_auth = base64.b64encode(username + ":" + password)

manager = EPNM(host, encoded_auth)

dev_addr_df = pd.read_csv('dev_address.csv')
connections_df = pd.read_csv('connections.csv')

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
	soft_type = getSWfromID(device_epnm_id)

	if soft_type == 'IOS-XE':
		devices[device_name] = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)

print devices

#add interfaces to the device objects
cols, rows = connections_df.shape

for j in range(0, rows+1):
	cur_dev = devices[connections_df.loc[i][0]]
	
	new_int_name = connections_df.loc[i][1]
	new_int_addr_mask = connections_df.loc[i][2]
	new_int_addr, new_int_mask = new_int_addr_mask.split('/')

	cur_dev.addInt(,)
	devices[connections_df.loc[i][0]]