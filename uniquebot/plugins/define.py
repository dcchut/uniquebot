from uniquebot.core.plugin import CorePlugin
from urllib import urlopen, quote
from lxml import etree, html
from re import sub

class Plugin(CorePlugin):
    bot = False

    def register(self,bot):
        self.bot = bot
        
    def striptags(self, text):
        return sub('<[^<]+?>', '', text)
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:3] == '.d '):
            w = quote(msg[3:].split()[0])
            u = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/' + w + '?key=' + quote('0ffe041c-4e69-48e1-8c88-3534f0c6dc1e')
            
            x = etree.parse(u).getroot()
            
            output = ''
            
            for t in x:
                # get the word being defined
                w = t.find('ew')
                
                if w is None:
                    continue
                    
                word = self.striptags(etree.tostring(w))
                
                output += word
                
                # what type of word is it?
                wt = t.find('fl')
                
                if wt is None:
                    continue
                   
                wordt = self.striptags(etree.tostring(wt))
                output += ' (' + wordt + ') '
                
                # get the definition(s)
                d = t.find('def')
                
                if d is None:
                    continue
                
                l = []
                c = 0
                cnt = 1
                
                for defi in d.findall('dt'):
                    # strip out the vi tags (and contents) and then remove the remaining tags (but leave contents)
                    tx = self.striptags(sub('<vi>.*?</vi>', '', etree.tostring(defi)))[1:].strip()
                    c += len(tx)
                    
                    if len(output) + c > 335:
                        break
                        
                    l.append(str(cnt) + '. ' + tx)
                    cnt += 1
                    
                    
                    
                output += ', '.join(l) + '. '
                
                if len(output) > 335:
                    break
               
            self.bot.say(channel,output)
                
                    
                    
                    