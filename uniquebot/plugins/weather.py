from uniquebot.core.plugin import CorePlugin
from urllib import urlopen
from twisted.internet import task
from time import time
import forecastio

class Plugin(CorePlugin):
    bot = False
    channels = {}
    upd = None
    
    def gettemp(self):
        # melbourne
        lat = -37.814251
        lng = 144.963165
        

        # try to get the current temperature
        try:
            forecast = forecastio.load_forecast(self.factory.cfg['weather']['api_key'], lat,lng, units='uk')
            curr = forecast.currently()
            return curr.temperature    
        except ValueError:
            # couldn't get the result, return something crazy
            return False
    
    def register(self,bot):
        # add our channel to be tracked
        self.channels[self.factory.channel] = [int(time()), self.gettemp()]
        self.bot = bot
        
        # run our weather updater every 5 minutes
        self.upd = task.LoopingCall(self.update)
        self.upd.start(60*5, False)
        
    def unregister(self, bot):
        # stop this looper
        self.upd.stop()
        self.upd = None
        
    def update(self):
        current_time = int(time())

        newtemp = self.gettemp()
                
        # couldn't get the temperature
        if (newtemp is False):
            return
                
        # do we need a weather update?
        for channel in self.channels:
            cd = self.channels[channel]
            
            # has the temperature changed by a 1.5 degrees?
            if (newtemp != cd[1] and (abs(newtemp - cd[1]) >= 1.5 or (current_time - cd[0] > 60*60*4))): 
                cd[0] = current_time
                self.bot.say(channel, "Weather update: " + str(cd[1]) + "C to " + str(newtemp) + "C")
                cd[1] = newtemp