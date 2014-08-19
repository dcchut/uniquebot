from uniquebot.core.plugin import CorePlugin
import pylast
from datetime import timedelta
from time import time

class Plugin(CorePlugin):
    network = None
    cache = {}
    
    def register(self,bot):
        self.network = pylast.LastFMNetwork(api_key = self.factory.cfg['lastfm']['api_key'], 
                                            api_secret = self.factory.cfg['lastfm']['api_secret'])
        
    def register_user(self,user,lfmuser):
        self.factory.c.execute('DELETE FROM ulastfm WHERE u = ?', (user,))
        self.factory.c.execute('INSERT INTO ulastfm (u,t) VALUES (?,?)', (user,lfmuser,))
        self.factory.db.commit()
        print 'registered', user, lfmuser
            
    def get_user(self,user):
        self.factory.c.execute('SELECT t FROM ulastfm WHERE u = ?', (user,))
        row = self.factory.c.fetchone()
        
        if row != None:
            return row[0]
        else:
            return None
            
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:4] == '.npr'):
            # register this user in the db
            self.register_user(user,msg[5:])
            return
            
        if (msg[:3] == '.np'):
            lfmuser = self.get_user(user)
            
            if lfmuser is None:
                return
                
            if lfmuser not in self.cache or (time()-self.cache[lfmuser][0]) > 60:
                u = self.network.get_user(lfmuser)
                
                # get their now playing track
                t = u.get_now_playing()
            
                # if we can't find their now playing track,
                # get the last track they played
                if t is None:
                    rpt = u.get_recent_tracks(1)
                    
                    # check if lastfm is being derpy
                    if len(rpt) == 0:
                        return
                    
                    # get the track played    
                    t = rpt[0].track
                    
                a = t.get_album()
                
                if a is not None:
                    a = a.title
                
                self.cache[lfmuser] = [time(),user,t.artist.name,t.title, t.get_duration(), a]

            # prepare output
            c = self.cache[lfmuser]
            
            out = c[1] + ' is listening to "' + c[3] + '" [' +  str(timedelta(milliseconds=c[4])) + '] by ' + c[2]
            
            if c[5] is not None:
                out += ' from album ' + c[5]
                
            self.bot.say(channel,out.encode('ascii','ignore'))