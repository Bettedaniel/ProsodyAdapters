class Ubuntu(object):
	def update(self):
		return ["sudo", "apt-get", "update", "-yy"]
	
	def upgrade(self):
		return ["sudo", "apt-get", "upgrade", "-yy"] 

	def install(self, install):
		standard = ["sudo", "apt-get", "install"]
		standard.extend([install])
		standard.extend(["-yy"])
		return standard

class OSX(object):
	def update(self):
		pass
	
	def upgrade(self):
		pass
	
	def install(self, install):
		pass	
