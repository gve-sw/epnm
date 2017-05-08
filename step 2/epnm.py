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

TEMPLATE ADDITIONS:
	Scroll down to the near bottom named "templateDeployMaster"
	From there you will see instructions to add a template function

"""

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

		self.templates = []

		temp_in = open('templates.in', 'r')
		for line in temp_in:
			line = line.rstrip('\n')
			self.templates.append(line)
		temp_in.close()
		print "Deploying templates from templates.in list:"
		print self.templates

	def getDevice(self, dev_id=''):
		#function returns device info for all devices managed by EPNM at self.ip
		getURL = self.url + 'data/Devices'

		if dev_id != '':
			getURL = getURL + '/' + str(dev_id) + '.json'
		else:
			getURL += '.json?.firstResult=0&.maxResults=400'

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)
		#print response.text
		return response

	def getIDfromIP(self, dev_mgmt_ip):
		#function takes manamgement ip address for a device and returns the unique EPNM ID
		dev_list_json = self.getDevice()
		dev_id_list = self.getDevIDs(dev_list_json)

		for i in reversed(dev_id_list):
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

	def formatJobTime(self, first_job, flag=False):

		firstJobName = first_job.split('jobName":"')
		firstJobName = firstJobName[1]
		firstJobName = firstJobName.split('",')
		#print firstJobName[0]
		firstJobTime = firstJobName[0].split('Devices')
		firstJobTime = firstJobTime[1]
		#print firstJobTime
		firstJobComponents = firstJobTime.split('_')
		year = firstJobComponents[-1]
		month = firstJobComponents[-3]
		day = firstJobComponents[-2]
		minute = firstJobComponents[1]
		seconds = firstJobComponents[2]
		hour = firstJobComponents[0]

		if firstJobComponents[4] == 'PM':
			if int(hour) < 12:
				new_hour = int(hour) + 12
				hour = str(new_hour)
		if flag == True:
			int_minute = int(minute)
			int_minute +=1
			minute = str(int_minute)
		
		sysTime = year + '-' + month + '-' + day + 'T' + hour + ':' + minute + ':' + seconds
		return sysTime		

	def verifyJobResult(self):

		f = open('output.txt', 'r')
		f.readline()
		f.readline()
		first_job = f.readline()

		first_job_time = self.formatJobTime(first_job)
		for line in f:
			if line == '\n':
				continue
			if line != '':
				last_job = line

		last_job_time = self.formatJobTime(last_job, True)
		f.close()

		querystring = '?jobName=startsWith("Job")&startTime=between("' + first_job_time + '","' + last_job_time + '")'

		getURL = self.url + 'op/jobService/runhistory.json' + querystring
		
		print "Printing Job Results into runHistory.txt using API Timestamps:"
		print getURL

		response = requests.get(getURL, headers=self.getHeaders, verify=self.verify)
		
		g = open('runHistory.txt', 'w')
		g.write(json.dumps(json.loads(response.text), indent=4))
		g.close()

		jobList = response.json()['mgmtResponse']['job']
		#print jobList

		success_count = 0
		fail_count = 0
		still_going = 0

		for dictionary in jobList:
			result = dictionary['runInstances']['runInstance']
			for key in result:
				#print key
				#print result[key]
				if key == 'resultStatus':
					result_status = result[key]
			#result_status = result['resultStatus']
			if result_status == 'SUCCESS':
				success_count +=1
			elif result_status == 'FAILURE':
				fail_count +=1
			else:
				still_going +=1

		total = success_count + fail_count
		print "Total jobs run: " + str(total)
		print "Success: " + str(success_count)
		print "Failure: " + str(fail_count)
		print "Still Running: " + str(still_going)

		return
		
	def deployTemplate(self, target_device, template_name, variable_payload=''):
		putURL = self.url + 'op/cliTemplateConfiguration/deployTemplateThroughJob.json'
		
		if variable_payload != '':
			payload = '{ "cliTemplateCommand" : { "targetDevices" : { "targetDevice" : { "targetDeviceID" : %s, "variableValues" : { "variableValue" : %s}}}, "templateName" : %s}}' % (target_device.epnm_id, variable_payload, template_name)


		else:
			payload = '{ "cliTemplateCommand" : { "targetDevices" : { "targetDevice" : {"targetDeviceID" : %s }},"templateName" : %s}}' % (target_device.epnm_id, template_name)
			#print "no payload"
		
		print 'Deployed %s template on %s' %(template_name, target_device.name)
		output = open('output.txt', 'a')
		output.write(payload)
		response = requests.put(putURL, headers=self.postHeaders, data=payload, verify=self.verify)
		output.write(template_name)
		output.write('\n')
		output.write(target_device.name)
		output.write('\n')
		output.write(response.text)
		output.write('\n\n')
		output.close()
		return response

	def currentTemplate(self, device_obj, XR_template, XE_template):
		device_type = device_obj.dev_type
		if device_type == 'ASR':
			cur_template = XR_template
		else:
			cur_template = XE_template
		return cur_template
	'''
	****************************************************************************************
	Edit below for changes/additions to template deployments
	Under templateDeploymentMaster create another "elif" statement before the "else"
	The elif name will need to match what is called within the templates.in file
	Then write a "response = self.____________(devices[dev])"
	The blank space will be the function called that will need to be written below

	For each template you wish to deploy, you will need to create one of these statements
	****************************************************************************************
	'''

	def templateDeploymentMaster(self, devices):
		for template_name in self.templates:
			for dev in devices:
				if template_name == ("Global CDP"):
					response = self.deployGlobalCDP(devices[dev])
				elif template_name == ("Interface CDP"):
					response = self.deployIntCDP(devices[dev])
				elif template_name == ("Interface Address"):
					response = self.deployIntAddr(devices[dev])
				elif template_name == ("Loopback Address"):
					response = self.deployLoopbackAddr(devices[dev])			
				elif template_name == ("OSPF"):
					response = self.deployOSPF(devices[dev])
				elif template_name == ("Global MPLS"):
					response = self.deployGlobalMPLS(devices[dev])
				elif template_name == ("Interface RSVP"):
					response = self.deployIntRSVP(devices[dev])			
				elif template_name == ("Global MPLS-TE"):
					response = self.deployGlobalMPLSTE(devices[dev])			
				elif template_name == ("Interface MPLS-TE"):
					response = self.deployIntMPLSTE(devices[dev])
				else:
					print "%s Template Not Found" %(template_name)

	'''
	************************************************************************************************************
	Below are the individual template deployment functions.

	The standard deployment consists of:
		def ______________(self, device_obj):
			cur_template = self.currentTemplate(device_obj, "XR ____________", "XE ____________")

			return self.deployTemplate(device_obj, cur_template)

	Additional coding may be required if the template utilizes variables such as IP addresses or interface names
	See "deployIntCDP" as an example

	The XR ________ or XE _________ names will have to exactly match the template name loaded within the EPNM
	currentTemplate is a function that discovers the device type and selects which template to deploy

	You will need to create a new function for each template you wish to deploy
	**************************************************************************************************************

	'''


	def deployGlobalCDP(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Global CDP", "XE Global CDP")

		return self.deployTemplate(device_obj, cur_template)

	def deployIntCDP(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Interface CDP", "XE Interface CDP")

		for key in device_obj.getInterface():
			if key == 'loopback0':
				#we don't enable CDP on the loopback interface
				continue
			else:
				cur_inter = device_obj.getInterface(key)
				var_load = '{"name": "%s", "value": "%s"}' % ('interfaceName', cur_inter.name)
				response = self.deployTemplate(device_obj, cur_template, var_load)
				#need to insert check here to make sure the response is positive

		return response

	def deployIntAddr(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Interface Address", "XE Interface Address")

		for key in device_obj.getInterface():
			if key == 'loopback0':
				continue
			else:
				cur_addr = device_obj.getInterface(key)
				cur_addr_str = cur_addr.addr
				var_load = '[{"name": "%s", "value": "%s"}, {"name": "%s", "value": "%s"}]' % ('interfaceName', key, 'ipAddress', cur_addr_str)
				self.deployTemplate(device_obj, cur_template, var_load)

	def deployLoopbackAddr(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Loopback Address", "XE Loopback Address")

		lo = device_obj.getInterface('loopback0')
		lo_addr = lo.addr
		var_load = '{"name": "%s", "value": "%s"}' % ('Loopback0', lo_addr)

		return self.deployTemplate(device_obj, cur_template, var_load)


	def deployOSPF(self, device_obj):
		device_type = device_obj.dev_type

		if device_type == 'ASR':
			lo0 = device_obj.getInterface('loopback0')
			for key in device_obj.getInterface():

				var_load = '[{"name": "%s", "value": "%s"}, {"name": "%s", "value": "%s"}]' % ('interfaceName', key, 'Loopback0', lo0.addr)
				self.deployTemplate(device_obj, "XR Interface OSPF", var_load)

		else:
			loAddr = device_obj.getInterface('loopback0')
			var_load = '{"name": "%s", "value": "%s" }' % ('Loopback0', loAddr.addr)
			self.deployTemplate(device_obj, "XE Global OSPF", var_load)
			for key in device_obj.getInterface():
				var_load = '{"name": "%s", "value": "%s" }' % ('interfaceName', key)
				self.deployTemplate(device_obj, "XE Interface OSPF", var_load)

	def deployGlobalMPLS(self, device_obj):
		device_type = device_obj.dev_type
		cur_template = self.currentTemplate(device_obj, "XR Global MPLS", "XE Global MPLS")

		if device_type == 'ASR':
			lo = device_obj.getInterface('loopback0')
			var_load = '{"name": "%s", "value": "%s"}' % ('Loopback0', lo.addr)
			self.deployTemplate(device_obj, cur_template, var_load)
		else:
			self.deployTemplate(device_obj, cur_template)

	def deployIntRSVP(self, device_obj, percent_value=100):
		#we need to determine where the percent values are coming from and
		#if they will be the same for all interfaces before continuing
		cur_template = self.currentTemplate(device_obj, "XR Interface RSVP", "XE Interface RSVP")

		for key in device_obj.getInterface():
			if key == 'loopback0':
				continue
			else:
				var_load = '[{"name": "%s", "value": "%s"}, {"name": "%s", "value": "%s"}]' % ('interfaceName', key, 'percentValue', percent_value)
				self.deployTemplate(device_obj, cur_template, var_load)

	def deployGlobalMPLSTE(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Global MPLS-TE", "XE Global MPLS-TE")

		self.deployTemplate(device_obj, cur_template)

	def deployIntMPLSTE(self, device_obj):
		cur_template = self.currentTemplate(device_obj, "XR Interface MPLS-TE", "XE Interface MPLS-TE")

		for key in device_obj.getInterface():
			if key == 'loopback0':
				continue
			else:
				var_load = '{"name": "%s", "value": "%s"}' % ('interfaceName', key)
				self.deployTemplate(device_obj, cur_template,var_load)



