from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	last_topscore = 0
	
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		if msg == '.points':
			bot.syncAllUsers(current_time)
			points = bot.getUserPoints(user)

			if points != None:
				bot.notice(user, "you have {0} points".format(str(points)))
				
			return True
		
		if msg == '.scores':
			bot.syncAllUsers(current_time)
			users = bot.getAllUsers()
			
			for row in users:
				if row.points == 0:
					continue
                
				bot.notice(user, "{0}: {1} points".format(row.user,row.points))
			return True
			
		if msg == '.topscore' and current_time - self.last_topscore >= 60:
			bot.syncAllUsers(current_time)
			users = bot.getAllUsers()
			
			for row in users[0:5]:
				bot.say(self.factory.channel, "{0}: {1} points".format(row.user, row.points))
			
			self.last_topscore = current_time
			return True
