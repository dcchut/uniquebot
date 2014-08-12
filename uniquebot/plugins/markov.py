from uniquebot.core.plugin import CorePlugin
from random import randint, random, choice

class Plugin(CorePlugin):
    def increaseWordCount(self, f, t):
        cond = (f.lower(),t.lower(),)
        self.factory.c.execute("SELECT o FROM markov WHERE f = ? AND t = ?", cond)
        row = self.factory.c.fetchone()
        
        if row is None:
            self.factory.c.execute("INSERT INTO markov (f,t,o) VALUES (?,?,1)", cond)
        else:
            self.factory.c.execute("UPDATE markov SET o = o + 1 WHERE f = ? AND t = ?", cond)
    
    def sayLine(self, channel, msg):
        wc = randint(4,12)
        if len(msg) > 0:
            words = [msg.split()[0]]
        else:
            words = [choice(['i', 'the', 'if'])]
        
        # now go through the database and collect the next word!
        while len(words) != wc:
            self.factory.c.execute("SELECT t, o FROM markov WHERE f = ?", (words[-1],))

            curr = {}
            for row in self.factory.c:
                curr[row[0].encode('ascii','ignore')] = float(row[1])
            
            if len(curr) == 0:
                break
            elif len(curr) == 1:
                words.append(curr.keys()[0])
            else:
                r  = random()
                rt = 0
                s  = sum(curr.values())
                
                for t in curr:
                    curr[t] = curr[t]/s
                
                for t in curr:
                    if r <= curr[t] + rt:
                        words.append(t)
                        break
                    else:
                        rt += curr[t]
        
        self.bot.say(channel, ' '.join(words))
    
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        if user == 'robbo' and msg[0:4] == '!say':
            self.sayLine(channel, msg[5:])
            return
        
        prev = None
        for word in msg.split():
            word = word.replace("'","")
            if not word.isalpha():
                prev = None
                continue
                
            if prev is None:
                prev = word
                continue
            # add a new word occurence
            self.increaseWordCount(prev, word)
            prev = word
            
        self.factory.db.commit()