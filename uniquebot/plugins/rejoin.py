from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
	def incoming(self, user, hostname, channel, msg, current_time, bot):
		if msg == "!rejoin":
            self.part(self.factory.channel)
            self.join(self.factory.channel)