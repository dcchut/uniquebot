#!/usr/bin/python
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
	last_ts  = 0
	maxtp    = 0
	
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
			
		current_time = int(time.time())
		user = user.split('!', 1)[0]
		
		# list points in console
		if msg == '!points':
			self.factory.c.execute("SELECT p FROM points WHERE h = ?", (user,))
			
			row = self.factory.c.fetchone()
			
			if row != None:
				self.notice(user, "you have " + str(row[0]) + " points remaining")
				
			return
		
		if msg == '!scores':
			self.syncAllUsers(current_time)
			
			for row in self.factory.c:
					p = str(row[0]).encode('ascii', 'ignore')
					h = str(row[1]).encode('ascii','ignore')
					self.notice(user, h + ": " + p + " points")
					time.sleep(0.5)
				
			return
		
		# topscore
		if msg == '!topscore':
			if current_time - self.last_ts >= 60:
				self.syncAllUsers(current_time)
					
				# now do the right thing
				self.factory.c.execute("SELECT p, h FROM points ORDER BY p DESC")
				counter = 0
				
				for row in self.factory.c:
					
					if counter == 5:
						break
						
					p = str(row[0]).encode('ascii', 'ignore')
					h = str(row[1]).encode('ascii','ignore')
					self.say(self.factory.channel, h + ": " + p + " points")
					counter += 1
				
				return
			
				self.last_ts = current_time
		
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
		
			points = self.syncUser(user, -1, current_time)
			
			# message
			nmsg = "repeated: "+original+", "+str(points)+" points remaining ("+hash[0:10]+")"
			
			# kick & notify them
			self.kick(self.factory.channel, user, "repeated " + original + ", " + str(points) + " points remaining (" + hash[0:10] + ")")
			self.notice(user, "warning, you repeated " + original + ", you have " + str(points) + " points remaining (" + hash[0:10] + ")")
			
			# add 1 point to the person who said this originally
			if (original != user):
				self.syncUser(original, 1, current_time)
			
			return
		
		# insert the text into the db
		self.factory.c.execute("INSERT INTO said (u, t) VALUES (?,?)",(user,hash,))
		self.factory.db.commit()

	def syncAllUsers(self, ctime):
		# sync all the records first
		self.factory.c.execute("SELECT h FROM points")
				
		for row in self.factory.c:
			self.syncUser(row[0], 0, ctime, True)
					
		# cheap hack
		self.factory.db.commit()
	
	def syncUser(self, user, points_delta, ctime, loop = False):
		# sync this user stuff :D
		c = self.factory.db.cursor()
		
		# get details about the points of this user
		c.execute("SELECT p, u FROM points WHERE h = ?", (user,))
		
		r = c.fetchone()
		
		# if the user has no record, give them a blank one
		if (r == None):
			c.execute("INSERT INTO points (h,p,u) VALUES (?,?,?)", (user, 0, ctime))
			
			if (not loop):
				self.factory.db.commit()
			
			r = (0, ctime)
			
		# calculate the new record
		points = r[0] + points_delta
		delta  = ctime - r[1]
		
		# have we gotten any points since the last update?
		tpdelta = delta / self.rate
		
		if (points_delta > 0):
			npoints = max(min(points+tpdelta, self.maxtp), points)
			
			if npoints == self.maxtp:
				update_time = ctime
			else:
				update_time = r[1] + self.rate * tpdelta
				
			points = npoints
		else:
			update_time = r[1]
			
		c.execute("UPDATE points SET p = ?, u = ? WHERE h = ?", (points, update_time, user))
		
		if (not loop):
			self.factory.db.commit()
		
		c.close()
		
		return points

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
