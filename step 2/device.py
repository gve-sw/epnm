from abc import ABCMeta

Class Device(object):

	__metaclass__ = ABCMeta

	self.interfaces = {}
	
	def __init__(self, name, mgmt_ip, loopback0, epnm_id):
		self.name = name
		self.mgmt_ip = mgmt_ip
		self.loopback0 = loopback0
		self.epnm_id = epnm_id

	def getName(self):
		#returns the name of the device (i.e. 4206 mid)
		return self.name

	def getMgmt_ip(self):
		#returns the management ip address of the device as a String
		return self.mgmt_ip

	@abstractmethod
	def getDev_type(self):
		#return a string that represents the type of device (i.e. ASR vs NCS)
		pass

	def getLoopback0(self):
		#returns a String that is the loopback ip address
		return self.loopback0

	def getEpnmId(self):
		#returns the unique identifier used by EPNM
		return self.epnm_id

	def addInt(self, int_name, int_add='x.x.x.x', int_mask='y.y.y.y')
		#adds interface to the device object (address and mask are optional)
		self.interfaces[int_name] = (int_add, int_mask)
		return

	def addIntAddr(self, int_name, int_add, int_mask):
		#adds or updates the address and mask for an interface
		self.interfaces[int_name] = (int_add, int_mask)
		return

	def getInterface(self, int_name='all'):
		#returns the information for a given interface, by default it returns all interfaces
		if int_name == 'all':
			return self.interfaces
		else:
			return self.interfaces[int_name]



Class ASR(Device):
	
	self.dev_type = 'ASR'

	def getDev_type(self):
		return self.dev_type

Class NCS(Device):

	self.dev_type = 'NCS'

	def getDev_type(self):
		return self.dev_typ