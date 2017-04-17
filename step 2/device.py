from abc import ABCMeta, abstractmethod

class Device(object):

	__metaclass__ = ABCMeta
	
	def __init__(self, name, mgmt_ip, loopback0, epnm_id, 
	interfaces = {}):
		self.name = name
		self.mgmt_ip = mgmt_ip
		self.epnm_id = epnm_id
		self.interfaces = interfaces
		self.addInt('loopback0', loopback0, 32)

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
		return self.interfaces['loopback0']

	def getEpnmId(self):
		#returns the unique identifier used by EPNM
		return self.epnm_id

	def addInt(self, int_name, int_add='x.x.x.x', int_mask=32):
		#adds interface to the device object (address and mask are optional)
		self.interfaces[int_name] = Interface(int_name, int_add, int_mask)
		return

	def addIntAddr(self, int_name, int_add, int_mask):
		#adds or updates the address and mask for an interface
		self.interfaces[int_name].updateAddr(int_add, int_mask)
		return

	def getInterface(self, int_name=''):
		#returns the information for a given interface, by default it returns all interfaces
		if int_name == '':
			return self.interfaces
		else:
			return self.interfaces[int_name]


class ASR(Device):

	def __init__(self):
		self.dev_type = 'ASR'
		Device.__init__()

	def getDev_type(self):
		return self.dev_type

class NCS(Device):

	def __init__(self, name, mgmt_ip, loopback0, epnm_id):
		self.dev_type = 'NCS'
		Device.__init__(self, name, mgmt_ip, loopback0, epnm_id)

	def getDev_type(self):
		return self.dev_typ

class Interface(object):

	def __init__ (self, name, addr, mask):
		self.name = name
		self.addr = addr
		self.mask = mask

	def updateAddr(self, newAddr, newMask):
		self.addr = newAddr
		self.mask = newMask

	def getIntName(self):
		return self.name

	def getIntAddr(self):
		return self.addr