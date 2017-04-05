import csv
import pandas as pd
import ./test_scripts/get_device_info.py
from device.py import Device, ASR, NCS

host = "198.18.134.7"
username = "user"
password = "Tester123"


dev_addr_df = pd.read_csv('dev_address.csv')
connections_df = pd.read_csv('connections.csv')

print dev_addr_df
print (" ")

num_rows = dev_addr_df.shape[1] + 1

devices = {}

for i in range(0, num_rows):
	device_name = dev_addr_df.loc[i]['Device Name']
	device_mgmt_ip = dev_addr_df.loc[i]['Mgmt']
	device_lo_ip = dev_addr_df.loc[i]['Loopback0']
	device_epnm_id = getID(device_mgmt_ip)
	soft_type = getSW(device_epnm_id)

	if soft_type == 'IOS-XE':
		devices[device_name] = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)

print devices