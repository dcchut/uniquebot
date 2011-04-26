# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time

# make sure only unique things are said
class UniqueBot(irc.IRCClient):
	nickname = "uniquebot"
	plugins = []
	plugins_registered = False

	def noticed(self, user, channel, msg):	
		print user, channel, msg

	# we've received a message
	def privmsg(self, user, channel, msg):	
		current_time = int(time.time())
		(user, hostname) = user.split('!',1)
		
		print user, channel, msg
		
		# for each plugin, do some magic!
		#for plugin in self.factory.plugins:
		#	plugin.incoming(user, hostname, channel, msg, current_time)
			
	# register a plugin with this module
	def registerPlugin(self, plugin):
		if plugin not in self.plugins:
			self.plugins.append(plugin)
			
			# put the factory into the plugin
			plugin.factory = self.factory
			
			# do we need to register any methods into this class?
			for method_name in plugin.register_methods:
				t = getattr(plugin, method_name)
				setattr(self, method_name, t)