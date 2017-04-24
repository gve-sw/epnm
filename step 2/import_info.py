import csv
import base64
import pandas as pd
import pprint
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
	#print device_lo_ip
	print "===============NEW ITERATION ====================="

	device_epnm_id = manager.getIDfromIP(device_mgmt_ip)
	soft_type = manager.getSWfromID(device_epnm_id)

	print '\n'
	print "printing devices dictionary now"
	for key in devices:
		print '\n'
		print key
		print devices[key]
		cur_dev = devices[key]
		#print cur_dev.name
		print "printing interfaces for device now"
		for ints in cur_dev.interfaces:
			print cur_dev.getInterface(ints)
			cur_int = cur_dev.getInterface(ints)
			print cur_int.name
			print cur_int.addr

	if soft_type == 'IOS-XE':
		#print(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
		temp_obj = NCS(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
		devices[device_name] = temp_obj
	else:
		devices[device_name] = ASR(device_name, device_mgmt_ip, device_lo_ip, device_epnm_id)
print 'Found all device IDs \n'

print '\n'
print '\n'
for key in devices:
	print '\n'
	print key
	print devices[key]
	cur_dev = devices[key]
	print cur_dev.name
	for ints in cur_dev.interfaces:
		print cur_dev.getInterface(ints)
		cur_int = cur_dev.getInterface(ints)
		print cur_int.name
		print cur_int.addr

print '\n'
print '\n'

#add interfaces to the device objects
rows, cols = connections_df.shape

def makeInts(conn_df, dev_dict, start):
	if start == 'A':
		idx = 0
		inc = 1
	else: 
		idx = 5
		inc = -1

	#print("Adding the " + start + " port")
	new_idx = connections_df.axes[1][idx]
	cur_dev = devices[connections_df.loc[j][new_idx]]

	#print "device port is assocaited with is: "
	#print cur_dev.name 

	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_name = connections_df.loc[j][new_idx]

	#print "Interface name to associate is: " + new_int_name

	idx += inc
	new_idx = connections_df.axes[1][idx]
	new_int_addr_mask = connections_df.loc[j][new_idx]

	#print "Address for the interface is: " + new_int_addr_mask
	new_list = new_int_addr_mask.split('/')
	new_int_addr, new_int_mask = new_list[0], new_list[1]


	cur_dev.addInt(new_int_name, new_int_addr, new_int_mask)
	return


for j in range(0, rows):
	#print "j is now " + str(j)
	makeInts(connections_df, devices, 'A')
	makeInts(connections_df, devices, 'Z')

print '\n'
print '\n'
print '\n'
for key in devices:
	print '\n'
	print key
	print devices[key]
	cur_dev = devices[key]
	print cur_dev.name
	for ints in cur_dev.interfaces:
		print cur_dev.getInterface(ints)
		cur_int = cur_dev.getInterface(ints)
		print cur_int.name
		print cur_int.addr

print '\n'
print '\n'

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

#template_order = ['XE Global CDP', 'XE Interface CDP', 'XE Loopback Address', 'XE Interface Address', 'XE Global OSPF', 'XE Interface OSPF', 'XE Global MPLS', 'XE Global MPLS-TE', 'XE Interface MPLS-TE', 'XE Interface RSVP']
print "About to call templateDeploymentMaster"
manager.templateDeploymentMaster(devices)
print "Returned from templateDeploymentMaster"
'''
for i in devices:
	response = manager.deployTemplate(devices[i].getEpnmId(), template_order[0])
	jobName = response.json()['mgmtResponse']['cliTemplateCommandJobResult']['jobName']

	job_resp = manager.verifyJobResult(jobName)
	manager.testVerify(jobName)
	#job_dict = job_resp.json()['mgmtResponse']
	#for key in job_dict:
		#print key
		#print job_dict[key]
'''
