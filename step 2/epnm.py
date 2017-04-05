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

	def getDevices(self):
		getUrl = self.url + 'data/Devices.json'
		response = requests.get(getUrl, auth=(self.user, self.password), verify=self.verify)
		return response

	