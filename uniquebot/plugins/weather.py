from uniquebot.core.plugin import CorePlugin
from urllib import urlopen

class Plugin(CorePlugin):
    last_weather_time = 0
    last_weather_temp = 0
    
    def gettemp(self):
        wt = urlopen("http://www.baywx.com/melbtemp.html")
        
        # magic :D
        return float(wt.readlines()[3][8:].split('&')[0])
    
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if self.last_weather_time == 0:
            self.last_weather_time = current_time
            self.last_weather_temp = self.gettemp()
        elif (current_time - self.last_weather_time > 60 * 10):
            newtemp = self.gettemp()
            self.last_weather_time = current_time
            if (newtemp != self.last_weather_temp):
                bot.say(channel, "weather update: " + str(self.last_weather_temp) + " to " + str(newtemp) + " degrees")
            self.last_weather_temp = newtemp