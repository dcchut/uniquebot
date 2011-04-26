from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	register_methods = ['isAuthedUser', 'kickedFrom']

	# put me in u
	def isAuthedUser(self, user):
		return user in self.auth and self.auth[user] == True
		
	# dont call me!
	def kickedFrom(self, channel, kicker, message):
		if channel == self.factory.channel:
			# if the kicker is authed, let them kick uis
			if not self.isAuthedUser(kicker):
				self.join(self.factory.channel)
	
	def register(self, bot):
		print "init test"
		bot.auth = {}