from uniquebot.core.plugin import CorePlugin
import urbandict

class Plugin(CorePlugin):
    bot = False
            
    def register(self,bot):
        self.bot = bot
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:3] == '.ud'):
            word = msg[4:]

            definition = urbandict.define(word)

            o = ''
            
            for d in definition:
                o += d['word'] + ' - ' + d['def'].strip().replace('\n', ' ')

                ex = d['example'].strip().replace('\n', ' ')

                if len(ex) > 0:                
                    o += ' - \x02' + d['example'].strip().replace('\n', ' ') +'\x02'
                break
            
            # output
            if len(o) > 0:
                if len(o) > 325:
                    o = o[:323] + '...'
                
                self.bot.say(channel, o[0:350].encode('ascii', 'ignore'))
