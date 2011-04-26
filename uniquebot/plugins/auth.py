from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	register_methods = ['isAuthedUser', 'kickedFrom', 'irc_RPL_WHOISUSER']
	
	def isAuthedUser(self, user):
		return user in self.bot.auth and self.bot.auth[user] == True
		
	def kickedFrom(self, channel, kicker, message):
		if channel == self.factory.channel:
			# if the kicker is authed, let them kick uis
			if not self.isAuthedUser(kicker):
				self.bot.join(self.factory.channel)

	def irc_RPL_WHOISUSER(self, prefix, params):
		# auth any waiting users
		if len(params) < 6:
			return
			
		user = params[1]
		
		if user in self.bot.auth:
			if params[-1] == 'robbo':
				self.bot.auth[user] = True
				self.bot.notice(user, "you have been authed")
				
	def register(self, bot):
		self.bot.auth = {}
		
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		if msg == '!auth':
			bot.auth[user] = False
			bot.whois(user)
			return True
	
		if msg == '!fuckoff' and self.isAuthedUser(user):
			self.factory.reconnect = False
			bot.quit('ordered to leave by ' + user)
			return True