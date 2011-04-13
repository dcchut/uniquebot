# uniquebot - by dcchut
# based on skeleton code by Twisted Matrix Laboratories 

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys, sqlite3, hashlib

# make sure only unique things are said
class UniqueBot(irc.IRCClient):
	nickname = "robbbot"
	have_joined = False
	
	def noticed(self, user, channel, msg):
		if (self.have_joined):
			return
						
		# want to wait until we are identified to get auto-ops
		# (i'm so lazy)
		if 'You are now identified' in msg:
			print "joining",self.factory.channel
			self.join(self.factory.channel)
			self.have_joined = True

	def signedOn(self):
		self.msg("nickserv", "identify " + self.factory.password)
		print "identifying with nickserv"
	
	def privmsg(self, user, channel, msg):
		if channel == self.nickname:
			# PM's can blow me
			return
		
		user = user.split('!', 1)[0]
		
		# take the lowercase version of the msg & remove trailing spaces & numbers
		msg = msg.lower().rstrip().rstrip("0123456789").rstrip()
		
		# hash dat shit
		hash = str(hashlib.sha224(msg).hexdigest())
		
		# has this been said before?
		self.factory.c.execute("SELECT u FROM said WHERE t = ?", (hash,))
		
		for row in self.factory.c:
			# kick dat ass
			uk = row[0].encode('ascii', 'ignore')
			self.kick(self.factory.channel, user, "repeated: "+uk+" ("+hash[0:10]+")")
			print "kicked ", user
			return
				
		# insert the text into the db
		self.factory.c.execute("INSERT INTO said (u, t) VALUES (?,?)",(user,hash,))
		self.factory.db.commit()

class UniqueBotFactory(protocol.ClientFactory):
	protocol = UniqueBot
	
	def __init__(self, password, channel, db):
		self.channel = channel
		self.password = password
		
		# open a "connection" to the sqlite db
		self.db = sqlite3.connect(db)
		
		# (maybe) create the table
		self.c = self.db.cursor()
		self.c.execute("CREATE TABLE IF NOT EXISTS said(u TEXT, t TEXT)")
		self.db.commit()
	
	def clientConnectionLost(self, connector, reason):
		# reconnect if disconnected
		connector.connect()
	
	def clientConnectionFailed(self, connector, reason):
		print "connection failed:", reason
		reactor.stop()

if __name__ == '__main__':
	# give me the password!
	if len(sys.argv) != 2:
		print "Usage: uniquebot.py <password>\n"
		sys.exit(1)
	
	# initialize logging
	log.startLogging(sys.stdout)
    
	# create factory protocol and application
	f = UniqueBotFactory(sys.argv[1], "#newvce", "db")

	# connect factory to this host and port
	reactor.connectTCP("irc.freenode.net", 6667, f)

	# run bot
	reactor.run()
