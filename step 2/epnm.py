import requests
import json
import contextlib
import base64

class EPNM(object):

	def __init__(self, ip, user_auth, verify=False):
		self.ip = ip
		self.verify = verify
		self.url = 'https://' + self.ip + '/webacs/api/v1/'
		self.authorization = "Basic " + encoded_auth

		self.getHeaders = {
			'authorization' : self.authorization,
			'cache-control': "no-cache"
		}

		self.postHeaders = {
			'authorization' : self.authorization,
			'cache-control': "no-cache",
			'content-type': "application/json"
		}

	def getDevice(self, dev_id=''):
		#function returns device info for all devices managed by EPNM at self.ip
		getURL = self.url + 'data/Devices'

		if dev_id != '':
			getURL = getURL + dev_id + '.json'
		else:
			getURL += '.json'

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)
		return response

	def deployTemplate(self, payload):
		#function deploys template through a job and returns the id for the job
		putUrl = self.url + 'op/cliTemplateConfiguration/deployTemplateThroughJob.json'

		response = requests.request("PUT", putUrl, data=payload, headers=self.postHeaders, verify=False)

		jobName = response.json()['mgmtResponse']['cliTemplateCommandJobResult']['jobName']

		return jobName

	def getIDfromIP(self, dev_mgmt_ip):
		#function takes manamgement ip address for a device and returns the unique EPNM ID
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
		#function returns a list of all device IDs managed by EPNM
		new_resp = devices_resp.json()['queryResponse']['entityId']

		IDs = []
		for entity in new_resp:
			IDs.append(entity['$'])

		return IDs

	def getSWfromID(self, dev_id):
		#function returns the software type for device provided
		dev_info_json = self.getDevice(dev_id)
		resp_list = dev_info_json.json()['queryResponse']['entity']
		dev_info_dict = resp_list[0]['devicesDTO']

		return dev_info_dict['softwareType']