import requests
import json
import contextlib
import base64
from pprint import pprint

class EPNM(object):

	requests.packages.urllib3.disable_warnings()

	xe_temp_deploy = ['XE Global CDP', 'XE Interface CDP', 'XE Interface Address', 'XE Loopback Address', 'XE Global OSPF', 'XE Interface OSPF', 'XE Global MPLS', 'XE Interface RSVP', 'XE Global MPLS-TE', 'XE Interface MPLS-TE']
	xr_temp_deploy = ['XR Global CDP', 'XR Interface CDP', 'XR Interface Address', 'XR Loopback Address', 'XR Interface OSPF', 'XR Dummy Temp', 'XR Global MPLS', 'XR Interface RSVP', 'XR Global MPLS-TE', 'XR Interface MPLS-TE']


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
		'''
	def deployTemplate(self, payload):
		#function deploys template through a job and returns the id for the job
		putUrl = self.url + 'op/cliTemplateConfiguration/deployTemplateThroughJob.json'

		response = requests.request("PUT", putUrl, data=payload, headers=self.postHeaders, verify=False)

		jobName = response.json()['mgmtResponse']['cliTemplateCommandJobResult']['jobName']

		return jobName
		'''
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

	def testVerify(self, jobName):

		url = "https://198.18.134.7/webacs/api/v1/op/jobService/runhistory.json"

		querystring = {"jobName":str(jobName)}
		print querystring

		#	querystring = {"jobName":"JobCliTemplateDeployIOSDevices10_27_59_612_PM_04_21_2017"}
		#	print querystring

		headers = {
		    'authorization': "Basic dXNlcjpUZXN0ZXIxMjM=",
		    'cache-control': "no-cache",
		    'postman-token': "6b9fdfb0-1fa7-7698-0e16-3dab07dd3004"
		    }

		response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

		print(response.text)

	def verifyJobResult(self, jobName):

		getURL = self.url + 'op/jobService/runhistory.json'

		querystring = {"jobName":jobName}
		
		response = requests.request("GET", getURL, headers=self.getHeaders, params=querystring, verify=self.verify)
		
		print response.text
		
		pprint(response.json())

		return response

	def deployTemplate(self, target_device, template_name, variable_payload=''):
		putURL = self.url + 'op/cliTemplateConfiguration/deployTemplateThroughJob.json'

		if variable_payload != '':
			payload = '{ "cliTemplateCommand" : { "targetDevices" : { "targetDevice" : { "targetDeviceID" : %s, "variableValues" : { "variableValue" : %s}}}, "templateName" : %s}}' % (target_device, variable_payload, template_name)
			print "Payload is " 
			print payload 

		else:
			payload = '{ "cliTemplateCommand" : { "targetDevices" : { "targetDevice" : {"targetDeviceID" : %s }},"templateName" : %s}}' % (target_device, template_name)
			print "no payload"

		response = requests.put(putURL, headers=self.postHeaders, data=payload, verify=self.verify)
		print response.text
		return response

	def templateDeploymentMaster(self, devices):

		print("Deploying global CDP")
		for dev in devices:
			print dev
			response = self.deployGlobalCDP(devices[dev])
			print response

		print("Deploying Int CDP")
		for dev in devices:
			print dev
			response = self.deployIntCDP(devices[dev])
			print response

		print("Deploying Int Addr")
		for dev in devices:
			print dev
			response = self.deployIntAddr(devices[dev])
			print response 

		print("Deploying Loopback Int")
		for dev in devices:
			print dev
			response = self.deployLoopbackAddr(devices[dev])
			print response

		print("Deploying OSPF")
		for dev in devices:
			print dev
			response = self.deployOSPF(devices[dev])
			print response

		print("Deploying Global MPLS")
		for dev in devices:
			print dev
			response = self.deployGlobalMPLS(devices[dev])
			print response

		print("Deploying Int RSVP")
		for dev in devices:
			print dev
			response = self.deployIntRSVP(devices[dev])
			print response

		print("Deploying Global MPLS-TE")
		for dev in devices:
			print dev
			response = self.deployGlobalMPLSTE(devices[dev])
			print response

		print("Deploying Int MPLS-TE")
		for dev in devices:
			print dev
			response = self.deployIntMPLSTE(devices[dev])
			print response




	def deployGlobalCDP(self, device_obj):
		device_type = device_obj.dev_type
		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[0]
		else:
			cur_template = self.xe_temp_deploy[0]

		return self.deployTemplate(device_obj.epnm_id, cur_template)

	def deployIntCDP(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[1]
		else:
			cur_template = self.xe_temp_deploy[1]

		for key in device_obj.getInterface():
			if key == 'loopback0':
				#we don't enable CDP on the loopback interface
				continue
			else:
				cur_inter = device_obj.getInterface(key)
				var_load = '{"name": %s, "value": %s }' % ('interfaceName', cur_inter.name)
				response = self.deployTemplate(device_obj.epnm_id, cur_template, var_load)
				#need to insert check here to ake sure the response is positive

		return response

	def deployIntAddr(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[2]
		else:
			cur_template = self.xe_temp_deploy[2]

		for key in device_obj.getInterface():
			cur_addr = device_obj.getInterface(key)
			cur_addr_str = cur_addr.addr
			var_load = '[{"name": %s, "value": %s}, {"name": %s, "value": %s}]' % ('interfaceName', key, 'ipAddress', cur_addr_str)
			self.deployTemplate(device_obj.epnm_id, cur_template, var_load)

	def deployLoopbackAddr(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[3]
		else:
			cur_template = self.xe_temp_deploy[3]

		lo = device_obj.getInterface('loopback0')
		lo_addr = lo.addr
		var_load = '{"name": %s, "value": %s }' % ('Loopback0', lo_addr)

		return self.deployTemplate(device_obj.epnm_id, cur_template, var_load)


	def deployOSPF(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			lo0 = device_obj.getInterface('loopback0')
			for key in device_obj.getInterface():

				var_load = '[{"name": %s, "value": %s}, {"name": %s, "value": %s}]' % ('interfaceName', key, 'Loopback0', lo0.addr)
				self.deployTemplate(device_obj.epnm_id, xr_temp_deploy[4], var_load)

		else:
			loAddr = device_obj.getInterface('loopback0')
			var_load = '{"name": %s, "value": %s }' % ('Loopback0', loAddr.addr)
			self.deployTemplate(device_obj.epnm_id, self.xe_temp_deploy[4], var_load)
			for key in device_obj.getInterface():
				var_load = '{"name": %s, "value": %s }' % ('interfaceName', key)
				self.deployTemplate(device_obj.epnm_id, self.xe_temp_deploy[5], var_load)

	def deployGlobalMPLS(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[6]
			lo = device_obj.getInterface('loopback0')
			var_load = '{"name": %s, "value": %s}' % 'Loopback0', lo.addr
		else:
			cur_template = self.xe_temp_deploy[6]
			self.deployTemplate(device_obj.epnm_id, cur_template)

	def deployIntRSVP(self, device_obj, percent_value=100):
		#we need to determine where the percent values are coming from and
		#if they will be the same for all interfaces before continuing
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[7]
		else:
			cur_template = self.xe_temp_deploy[7]

		for key in device_obj.getInterface():
				if key == 'loopback0':
					continue
				else:
					var_load = '[{"name": %s, "value": %s}, {"name": %s, "value": %s}]' % ('interfaceName', key, 'percentValue', percent_value)
					self.deployTemplate(device_obj.epnm_id, cur_template, var_load)

	def deployGlobalMPLSTE(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[8]
		else:
			cur_template = self.xe_temp_deploy[8]

		self.deployTemplate(device_obj.epnm_id, cur_template)

	def deployIntMPLSTE(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			cur_template = self.xr_temp_deploy[9]
		else:
			cur_template = self.xe_temp_deploy[9]

		for key in device_obj.getInterface():
			var_load = '{"name": %s, "value": %s}' % ('interfaceName', key)
			self.deployTemplate(device_obj.epnm_id, cur_template,var_load)



