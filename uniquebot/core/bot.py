# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sqlite3

# make sure only unique things are said
class UniqueBot(irc.IRCClient):
	nickname = "robbbot"
	plugins = []
	plugins_registered = False
	
	def signedOn(self):
		# do our own magic here
		self.msg("nickserv", "identify {0}".format(self.factory.password))
		self.join(self.factory.channel)
		
		# register these mofos
		if self.plugins_registered == False:
			self.plugins_registered = True
			
			for plugin in self.factory.plugins:
				self.registerPlugin(plugin)

	def noticed(self, user, channel, msg):	
		print user, channel, msg

	# we've received a message
	def privmsg(self, user, channel, msg):	
		current_time = int(time.time())
		(user, hostname) = user.split('!',1)
		
		print user, channel, msg
		
		# for each plugin, do some magic!
		for plugin in self.plugins:
			plugin.incoming(user, hostname, channel, msg, current_time, self)
			
	# register a plugin with this module
	def registerPlugin(self, plugin):
		if plugin not in self.plugins:
			self.plugins.append(plugin)
			
			# put the factory into the plugin
			plugin.factory = self.factory
			plugin.register(self)
			
			# do we need to register any methods into this class?
			for method_name in plugin.register_methods:
				t = getattr(plugin, method_name)
				setattr(self, method_name, t)
			
class UniqueBotFactory(protocol.ClientFactory):
	protocol = UniqueBot
	reconnect = True
	
	def __init__(self, password, channel, db, plugins):
		self.channel = channel
		self.password = password
		self.plugins = plugins
		
		# open a "connection" to the sqlite db 
		self.db = sqlite3.connect(db)
		
		# (maybe) create the table
		self.c = self.db.cursor()
		self.c.execute("CREATE TABLE IF NOT EXISTS said(u TEXT, t TEXT)")
		self.c.execute("CREATE TABLE IF NOT EXISTS points(h TEXT, p INTEGER, u INTEGER)")
		self.db.commit()
	
	def clientConnectionLost(self, connector, reason):
		# only reconnect if we haven't been issued a quit
		if (self.reconnect):
			connector.connect()
		else:
			reactor.stop()

	
	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()