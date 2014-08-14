class CorePlugin():
	register_methods = []
	
	def __init__(self, plugin_name, plugin_internal_name, plugin_module):
		self.plugin_name = plugin_name
		self.plugin_internal_name = plugin_internal_name
		self.plugin_module = plugin_module
	
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		# do something here
		return
		
	def register(self, bot):
		# maybe do something upon registration?
		return
		
	def unregister(self, bot):
		# maybe do something when we unregister?
		return