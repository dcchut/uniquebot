from uniquebot.core.plugin import CorePlugin
from urllib import urlopen, quote
from lxml import etree, html
from re import sub
from nltk.corpus import wordnet

class Plugin(CorePlugin):
    bot = False

    def register(self,bot):
        self.bot = bot
        
    def striptags(self, text):
        return sub('<[^<]+?>', '', text)
        
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if (msg[:3] == '.d '):
            w = quote(msg[3:].split()[0])
            
            synsets = wordnet.synsets(w)
            output = w + ' -'
            mod = False
            
            for synset in synsets:
                obuffer = ' [' + synset.pos + '] ' + synset.definition + ', '
                
                if len(output) + len(obuffer) > 365:
                    break
                    
                output += obuffer 
                mod = True
                
            if mod is True:
                self.bot.say(channel,output[:-2])