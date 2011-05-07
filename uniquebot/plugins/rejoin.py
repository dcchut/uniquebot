from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		if msg == "!rejoin" and bot.isAuthedUser(user):
			bot.leave(self.factory.channel)
			bot.join(self.factory.channel)
