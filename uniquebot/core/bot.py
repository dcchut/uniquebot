# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log
from nltk.corpus import wordnet

# system imports
import time, sqlite3, sys

# make sure only unique things are said
class UniqueBot(irc.IRCClient):
	nickname = "uniquebot"
	plugins = []
	plugins_registered = False
	
	# do some magic signon stuff here, & register the plugins
	def signedOn(self):
		# do our own magic here
		self.setNick(self.factory.nickname)
		time.sleep(5)
		
		self.msg("nickserv", "identify {0}".format(self.factory.password))
		time.sleep(2)
		self.join(self.factory.channel)
		
		# register these mofos
		if self.plugins_registered == False:
			self.plugins_registered = True
			
			for plugin in self.factory.plugins.values():
				self.registerPlugin(plugin)
	
	# skeleton notice logging
	def noticed(self, user, channel, msg):	
		print user, channel, msg

	# we've received a message
	def privmsg(self, user, channel, msg):	
		current_time = int(time.time())
		(user, hostname) = user.split('!',1)
		
		print user, channel, msg
		
		# would like to make this a plugin,
		# but then weird things might happen!
		if (user == 'robbo' and msg == '.reload'):
			print 'starting plugin reload'
			self.factory.reloadPlugins(self)
			print 'finished plugin reload'
		
		# for each plugin, do some magic!
		for plugin in self.plugins:
			plugin.incoming(user, hostname, channel, msg, current_time, self)
			
	# register a plugin with this module
	def registerPlugin(self, plugin):
		if plugin not in self.plugins:
			self.plugins.append(plugin)
			
			# put the factory into the plugin
			plugin.factory = self.factory
			plugin.bot = self
			plugin.register(self)

			# do we need to register any methods into this class?
			for method_name in plugin.register_methods:
				t = getattr(plugin, method_name)
				setattr(self, method_name, t)
				
			print "loaded plugin {0}".format(str(plugin))
			
	def unregisterPlugin(self, plugin):
		# nothing to unregister
		if plugin not in self.plugins:
			return
			
		# remove the registered methods
		for method_name in plugin.register_methods:
			delattr(self, method_name)
		
		# deregister the plugin
		plugin.unregister(self)
		
		# remove the plugin from our loaded plugins list
		self.plugins.remove(plugin)
		
		print "unregistered plugin {0}".format(str(plugin))
		
class UniqueBotFactory(protocol.ClientFactory):
	protocol = UniqueBot
	reconnect = True
	
	def __init__(self, nickname, password, channel, db, plugins, cfg):
		self.channel = channel
		self.password = password
		self.plugins = plugins
		self.nickname = nickname
		self.cfg = cfg
		
		# open a "connection" to the sqlite db 
		self.db = sqlite3.connect(db)
		
		print 'loading wordnet'
		synsets = wordnet.synsets('cake')
		print 'loaded wordnet'
		
		# (maybe) create the table
		self.c = self.db.cursor()
		self.c.execute("CREATE TABLE IF NOT EXISTS said(u TEXT, t TEXT)")
		self.c.execute("CREATE TABLE IF NOT EXISTS points(h TEXT, p INTEGER, u INTEGER)")
		self.c.execute("CREATE TABLE IF NOT EXISTS markov(f TEXT, t TEXT, o INTEGER)")
		self.c.execute("CREATE TABLE IF NOT EXISTS ulastfm(u TEXT, t TEXT)")
		self.db.commit()
	
	def reloadPlugins(self, bot):
		plugins = {}
		
		for plugin in self.plugins.values():
			# unregister each plugin with the bot
			bot.unregisterPlugin(plugin)
			
			# reload the module
			reload(sys.modules[plugin.plugin_module])
			
			# get a new instance
			plugins[plugin.plugin_name] = sys.modules[plugin.plugin_module].Plugin(plugin.plugin_name, plugin.plugin_internal_name, plugin.plugin_module)
			
			# delete old instance
			del plugin
		
		# now register each of the new plugins
		for plugin in plugins.values():
			bot.registerPlugin(plugin)
			
		# update this bad boy
		self.plugins = plugins
		
	def clientConnectionLost(self, connector, reason):
		# only reconnect if we haven't been issued a quit
		if (self.reconnect):
			connector.connect()
		else:
			reactor.stop()

	
	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		
		# attempt to reconnect
		connector.connect()
				
		#reactor.stop()