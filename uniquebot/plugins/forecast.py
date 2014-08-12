from uniquebot.core.plugin import CorePlugin
import forecastio
from forecastio.utils import PropertyUnavailable

from geopy import geocoders
from geopy import distance

class Plugin(CorePlugin):
    bot = False
    
    def register(self,bot):
        self.bot = bot
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:8] == '.weather'):
            # optional location specifier
            location = msg[9:].strip()
            
            if (location == 'smad'):
                location = 'Austin, TX'
            elif (location == 'caramel'):
                location = 'Columbus, OH'
            elif (len(location) == 0):
                location = 'Melbourne, 3000'
                
            g = geocoders.GoogleV3()
            
            try:
                u = g.geocode(location, exactly_one=False)
            except geocoders.googlev3.GQueryError:
                return
                
            if (u is None):
                return
                
            # find the closest record to Melbourne
            mel = (-37.8152065, 144.963937)
            
            ltx = u[0][0]
            lat = u[0][1][0]
            lng = u[0][1][1]
            
            for ltxt, (latt, lngt) in u:
                d = distance.distance(mel, (latt,lngt)).km
                
                # priotise this record
                if (d < 200):
                    ltx = ltxt
                    lat = latt
                    lng = lngt
                    
                    break
            
            # now get the weather records
            forecast = forecastio.load_forecast(self.factory.cfg['weather']['api_key'], lat,lng, units='uk')
    
            curr = forecast.currently()
            
            # format it
            fstring = 'Weather for ' + ltx + ' | ' + curr.summary + ', ' + str(round(curr.temperature,1)) + 'C, '
           
            fstring += str(curr.humidity * 100) + '% humidity'
            
            try:
                fstring += ', wind ' + str(round(curr.windspeed * 1.60934,1)) + ' kmph'
            except PropertyUnavailable:
                pass
           
            # output
            self.bot.say(channel,fstring.encode('ascii','ignore'))