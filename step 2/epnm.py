import requests
import json
import contextlib

Class EPNM(object):

	self.url = ''

	def __init__(self, ip, user, password, verify=False):
		self.ip = ip
		self.user = user
		self.password = password
		self.verify = verify
		self.url = 'https://' + self.ip + '/webacs/api/v1/'

	def getDevice(self, dev_id=''):
		getURL = self.url + 'data/Devices'

		if dev_id != '':
			getURL = getURL + dev_id + '.json'
		else:
			getURL += '.json'

		response = requests.get(getURL, auth=(self.user, self.password), verify=self.verify)
		return response

	def getIDfromIP(self, dev_mgmt_ip):

		dev_list_json = self.getDevices()
		dev_id_list = self.getDevIDs(dev_list_json)

		for i in dev_id_list:

			dev_info_json = self.getDevice(i)
			
			resp_list = dev_info_json.json()['queryResponse']['entity']
			dev_info_dict = resp_list[0]['devicesDTO']
			
			if dev_info_dict['ipAddress'] == dev_mgmt_ip:
				return dev_info_dict['deviceId']
		
		return "No such device found"


	def getDevIDs(self, devices_resp):

		new_resp = devices_resp.json()['queryResponse']['entityId']

		IDs = []
		for entity in new_resp:
			IDs.append(entity['$'])

		return IDs

	def getSWfromID(self, dev_id):

		dev_info_json = self.getDevice(dev_id)
		resp_list = dev_info_json.json()['queryResponse']['entity']
		dev_info_dict = resp_list[0]['devicesDTO']

		return dev_info_dict['softwareType']