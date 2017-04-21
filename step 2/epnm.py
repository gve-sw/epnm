import requests
import json
import contextlib
import base64
from pprint import pprint

class EPNM(object):

	requests.packages.urllib3.disable_warnings()

	def __init__(self, ip, user_auth, verify=False):
		self.ip = ip
		self.verify = verify
		self.url = 'https://' + self.ip + '/webacs/api/v1/'
		self.authorization = "Basic " + user_auth

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
			getURL = getURL + '/' + str(dev_id) + '.json'
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
		dev_list_json = self.getDevice()
		dev_id_list = self.getDevIDs(dev_list_json)

		for i in dev_id_list:
			dev_info_json = self.getDevice(i)
			resp_list = dev_info_json.json()['queryResponse']['entity']
			dev_info_dict = resp_list[0]['devicesDTO']
			if dev_info_dict['ipAddress'] == dev_mgmt_ip:
				return dev_info_dict['@id']
		
		print '\n \n \n'
		print '=================================================================='
		print '=====================                        ====================='
		print '*********************  NO SUCH DEVICE FOUND  *********************'
		print '=====================                        ====================='
		print '=================================================================='
		print '\n \n \n'

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



	def getTemplateInfo(self):
		getURL = self.url + '/data/CliTemplate.json'

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)
		count = response.json()['queryResponse']['@count']
		getURL = self.url + 'data/CliTemplate.json?.full=true&.firstResult=0&.maxResults=' + count

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)

		entity_dict = response.json()['queryResponse']['entity']

		InfoKeys = ['name', 'templateID', 'path']
		TemplateInfoDict = {}

		for temp_dicts in entity_dict:
			entity_subdict = temp_dicts['cliTemplateDTO']

			tempID = entity_subdict['templateId']
			if 'name' in entity_subdict:
				tempName = entity_subdict['name']
			else:
				tempName = 'No Name Found'
			if 'path' in entity_subdict:
				tempPath = entity_subdict['path']
			else:
				tempPath = 'No Path Found'

			TemplateInfoDict[tempID] = [tempName, tempPath]

		return TemplateInfoDict

	def getTemplate(self, tid):
		getURL = self.url + 'data/CliTemplate/' + str(tid) + '.json'

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)

		return response

	'''def getTemplatePath(self, temp_json):
		temp_resp = temp_json.json()['queryResponse']['entity']

		DTO_dict = temp_resp[0]['cliTemplateDTO']

		path = 'no path found'
		for k in DTO_dict:
			if k == 'path':
				path = DTO_dict['path']

		return path'''
