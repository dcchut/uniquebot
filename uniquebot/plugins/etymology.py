from uniquebot.core.plugin import CorePlugin
from urllib import urlopen, quote
from lxml import etree, html
from HTMLParser import HTMLParser
from re import sub

class Plugin(CorePlugin):
    bot = False

    def register(self,bot):
        self.bot = bot
        
    def striptags(self, text):
        return sub('<[^<]+?>', '', text)
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:5] == '.ety '):
            w = quote(msg[5:].split()[0])
            
            url = 'http://www.etymonline.com/index.php?allowed_in_frame=0&search=' + quote(w) + '&searchmode=term'
            ety = html.parse(url)
            dic = ety.getroot().get_element_by_id('dictionary')
            
            # get definition root
            dt = dic.xpath("//dt[1]")
            
            if len(dt) >= 1:
                dt_text = self.striptags(HTMLParser().unescape(html.tostring(dt[0]))).strip()
                
                dd = dic.xpath("//dd[1]")
                dd_text = self.striptags(HTMLParser().unescape(html.tostring(dd[0]))).strip()
                
                buffer = dt_text + ' - ' + dd_text
                
                if len(buffer) > 250:
                    buffer = buffer[:250] + '...'
                
                self.bot.say(channel,buffer.encode('ascii', 'ignore'))