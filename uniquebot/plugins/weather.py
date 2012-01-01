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
        
        # do we need a weather update?
        for channel in self.channels:
            cd = self.channels[channel]
            
            # has 25 minutes elapsed?
            if (current_time - cd[0] > 60*25):
                newtemp = self.gettemp()
                if (newtemp != cd[1]):
                    cd[0] = current_time
                    self.bot.say(channel, "weather update: " + str(cd[1]) + " to " + str(newtemp) + " degrees")
                    cd[1] = newtemp