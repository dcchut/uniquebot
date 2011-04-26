from twisted.internet import reactor, protocol
from uniquebot.core.bot import UniqueBot
import sqlite3

class UniqueBotFactory(protocol.ClientFactory):
	protocol = UniqueBot
	reconnect = True
	
	def __init__(self, nickname, password, channel, db, plugins):
		self.nickname = nickname
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