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
	nickname = "robbbot" # nickname of the bot
	auth 	 = {} 		 # list of (potential) authenticated users
	rate     = 60 * 60 	 # an hour between point increments
	pdefault = 3 		 # default number of points
	
	def noticed(self, user, channel, msg):					
		# want to wait until we are identified to get auto-ops
		# (i'm so lazy)
		if 'You are now identified' in msg:
			print "joining",self.factory.channel
			self.join(self.factory.channel)
			
		print user, channel, msg

	def signedOn(self):
		self.msg("nickserv", "identify " + self.factory.password)
		print "identifying with nickserv"
	
	def privmsg(self, user, channel, msg):
		if channel == self.nickname:
			# PM's can blow me
			return
		
		host = user.split('!', 1)[1]
		user = user.split('!', 1)[0]
		
		# do a login
		if msg == '!auth':
			# use a whois to auth 
			self.auth[user] = False		
			self.whois(user)
			return
			
		# leave
		if msg == '!fuckoff' and user in self.auth and self.auth[user] == True:
			self.factory.reconnect = False
			self.quit('ordered to leave by ' + user)
			return
		
		# take the lowercase version of the msg & remove trailing spaces & numbers
		msg = msg.lower().rstrip().rstrip("0123456789").rstrip()
		
		# hash dat shit
		hash = str(hashlib.sha224(msg).hexdigest())
		
		# has this been said before?
		self.factory.c.execute("SELECT u FROM said WHERE t = ?", (hash,))
		
		row = self.factory.c.fetchone()

		if row != None:
			# original user who said this line
			original = row[0].encode('ascii', 'ignore')
		
			# find details about the points of this user
			self.factory.c.execute("SELECT p, u FROM points WHERE h = ?", (host,))
			
			host_points  = self.factory.c.fetchone()
			current_time = int(time.time())
			 
			if (host_points == None):
				# insert a new record & commit
				self.factory.c.execute("INSERT INTO points (h, p, u) VALUES (?,?,?)", (host,self.pdefault,current_time))
				self.factory.db.commit()
				
				# store the real data in here
				host_points = (self.pdefault, current_time)
				
			# actual points
			points = host_points[0] - 1
			delta  = current_time - host_points[1];
			
			# have we accrued any points since the last update?
			points_delta = delta / self.rate

			if (points_delta > 0):
				new_points = min(points + points_delta, self.pdefault)
				
				if new_points == self.pdefault:
					update_time = current_time
				else:
					# how soon after the last update would this user have accrued
					# the correct number of points? don't wany to set to current_time,
					# as this may have occured in the past
					update_time = host_points[1] + self.rate * (points_delta)
				
				points = new_points
					
				self.factory.c.execute("UPDATE points SET p = ?, u = ? WHERE h = ?", (points, update_time, host))
			else:
				self.factory.c.execute("UPDATE points SET p = ? WHERE h = ?", (points, host))
			
			self.factory.db.commit()
			
			# message
			nmsg = "repeated: "+original+", "+str(points)+" points remaining ("+hash[0:10]+")"
			
			# if they have no points remaining, kick them
			if points <= 0:
				self.kick(self.factory.channel, user, "repeated " + original + ", " + str(points) + " points remaining (" + hash[0:10] + ")")
							
			self.notice(user, "warning, you repeated " + original + ", you have " + str(points) + " points remaining (" + hash[0:10] + ")")
			
			return
		
		# insert the text into the db
		self.factory.c.execute("INSERT INTO said (u, t) VALUES (?,?)",(user,hash,))
		self.factory.db.commit()

	def irc_RPL_WHOISUSER(self, prefix, params):
		# auth any waiting users
		if len(params) < 6:
			return
			
		user = params[1]
		
		if user in self.auth:
			if params[-1] == 'robbo':
				self.auth[user] = True
				self.notice(user, "you have been authed")

class UniqueBotFactory(protocol.ClientFactory):
	protocol = UniqueBot
	reconnect = True
	
	def __init__(self, password, channel, db):
		self.channel = channel
		self.password = password
		
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

if __name__ == '__main__':
	# give me the password!
	if len(sys.argv) != 5:
		print "Usage: uniquebot.py <server[:port]> <channel> <dbfile> <password>\n"
		sys.exit(1)
	
	# initialize logging
	log.startLogging(sys.stdout)
    
	# create factory protocol and application
	f = UniqueBotFactory(sys.argv[4], sys.argv[2], sys.argv[3])

	# split server in server & port
	c = sys.argv[1].split(':')
	
	if len(c) == 1:
		port = 6667
	else:
		port = c[1]

	# connect factory to this host and port
	reactor.connectTCP(c[0], port, f)

	# run bot
	reactor.run()
