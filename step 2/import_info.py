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

num_rows = dev_addr_df.shape[1]
devices = {}


#create the device objects
for i in range(0, num_rows):
	device_name = dev_addr_df.loc[i]['Device Name']
	device_mgmt_ip = dev_addr_df.loc[i]['Mgmt']
	device_lo_ip = dev_addr_df.loc[i]['Loopback0']

	device_epnm_id = manager.getIDfromIP(device_mgmt_ip)
	soft_type = manager.getSWfromID(device_epnm_id)

	if soft_type == 'IOS-XE':
		devices[device_name] = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
print 'Found all device IDs \n'
#print devices


#add interfaces to the device objects
rows, cols = connections_df.shape

def makeInts(conn_df, dev_dict, start):
	if start == 'A':
		idx = 0
		inc = 1
	else: 
		idx = 5
		inc = -1

	new_idx = connections_df.axes[1][idx]
	cur_dev = devices[connections_df.loc[j][new_idx]]

	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_name = connections_df.loc[j][new_idx]

	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_addr_mask = connections_df.loc[j][new_idx]

	new_list = new_int_addr_mask.split('/')
	new_int_addr, new_int_mask = new_list[0], new_list[1]


	cur_dev.addInt(new_int_name, new_int_addr, new_int_mask)
	return


for j in range(0, rows):
	makeInts(connections_df, devices, 'A')
	makeInts(connections_df, devices, 'Z')

print 'About to get Template Info \n'

temp_info_dict = manager.getTemplateInfo()

print 'Got Template Info'

XE_template_info = {}
XR_template_info = {}

for key in temp_info_dict:
	if 'My Templates/X' in temp_info_dict[key][1]:
		if 'XE' in temp_info_dict[key][1]:
			XE_template_info[key] = temp_info_dict[key]
		elif 'XR' in temp_info_dict[key][1]:
			XR_template_info[key] = temp_info_dict[key]



