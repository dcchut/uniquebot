from uniquebot.core.plugin import CorePlugin
from time import time
import requests
from datetime import datetime
from geopy import geocoders

class Plugin(CorePlugin):
    bot = False
            
    def register(self,bot):
        self.bot = bot
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:5] == '.time' or msg[:2] == '.t'):
            # get the optional location
            location = ' '.join(msg.split()[1:]).strip()
            
            if (location == 'smad'):
                location = 'Austin, TX'
            elif (location == 'caramel'):
                location = 'Columbus, OH'
            elif (len(location) == 0):
                location = 'Melbourne'
            
            g = geocoders.GoogleV3()
            
            # handle when someone writes a rubbish location
            try:
                u = g.geocode(location, exactly_one=False)
            except geocoders.googlev3.GQueryError:
                return
                
            # get the first record; probably the correct one
            if (len(u) > 0):
                u = u[0]
            
            timestamp = int(time())
            
            payload = {'location': ','.join(map(str,u[1])),
                       'timestamp': str(timestamp),
                       'sensor' : 'false' }
                       
            r = requests.get('https://maps.googleapis.com/maps/api/timezone/json', params = payload)
            j = r.json()
            
            # get the local time
            dt = datetime.utcfromtimestamp(timestamp + j['dstOffset'] + j['rawOffset'])
            
            fstring = 'Time in ' + u[0].encode('ascii', 'ignore') + ' is ' + dt.strftime('%I:%M%p')
                
            # output
            self.bot.say(channel,fstring)
