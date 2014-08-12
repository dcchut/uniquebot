from uniquebot.core.plugin import CorePlugin
import hashlib

class Plugin(CorePlugin):
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		if msg[0] == "!":
			return
			
		# clean it up
		msg = msg.lower().rstrip().rstrip("0123456789").rstrip()
		
		# hash dat shit
		hash = str(hashlib.sha224(msg).hexdigest())
		
		# have we said this before?
		original = self.getLine(hash)
		
		if original != None:
			# take a point off the user
			points = bot.syncUser(user, -1, current_time)
			
			# message
			bot.notice(user, "warning, you repeated {0}, you have {1} points ({2})".format(original.user, str(points), hash[0:10]))
			
			# add a point to user who said this originally
			if original.user != user:
				bot.syncUser(original, 1, current_time)
		else:
			# otherwise insert the text into the DB
			self.insertLine(user, hash)
			
			# sync them (if they dont have a user record!)
			bot.syncUser(user, 0, current_time)
			

	def insertLine(self, user, hash):
		self.factory.c.execute("INSERT INTO said (u, t) VALUES (?,?)", (user,hash,))
		self.factory.db.commit()
		
	def getLine(self, hash):
		self.factory.c.execute("SELECT u FROM said WHERE t = ?", (hash,))
		row = self.factory.c.fetchone()
		
		if row != None:
			# return the original user who said this line
			return self.bot.getUser(str(row[0]).encode('ascii','ignore'))
		else:
			return None