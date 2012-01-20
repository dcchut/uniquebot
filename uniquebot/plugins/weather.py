from uniquebot.core.plugin import CorePlugin
from urllib import urlopen
from twisted.internet import task
from time import time

class Plugin(CorePlugin):
    bot = False
    channels = {}

    def gettemp(self):
        wt = urlopen("http://www.baywx.com/melbtemp.html")
        
        # magic :D
        return float(wt.readlines()[3][8:].split('&')[0])
    
    def register(self,bot):
        # add our channel to be tracked
        self.channels[self.factory.channel] = [int(time()), self.gettemp()]
        self.bot = bot
        
        # run our weather updater every 5 minutes
        task.LoopingCall(self.update).start(60*5,False)
    
    def update(self):
        current_time = int(time())
        newtemp = self.gettemp()
                
        # do we need a weather update?
        for channel in self.channels:
            cd = self.channels[channel]
            
            # has the temperature changed by a 1.5 degrees?
            if (newtemp != cd[1] and (abs(newtemp - cd[1]) >= 1.5 or (current_time - cd[0] > 60*60*4))): 
                cd[0] = current_time
                self.bot.say(channel, "weather update: " + str(cd[1]) + " to " + str(newtemp) + " degrees")
                cd[1] = newtemp