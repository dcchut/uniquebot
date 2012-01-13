from uniquebot.core.plugin import CorePlugin

class Plugin(CorePlugin):
    def increaseWordCount(self, f, t):
        cond = (f,t,)
        print cond
        self.factory.c.execute("SELECT o FROM markov WHERE f = ? AND t = ?", cond)
        row = self.factory.c.fetchone()
        
        if row is None:
            self.factory.c.execute("INSERT INTO markov (f,t,o) VALUES (?,?,1)", cond)
        else:
            self.factory.c.execute("UPDATE markov SET o = o + 1 WHERE f = ? AND t = ?", cond)
    
    def incoming(self, user, hostname, channel, msg, current_time, bot):
        prev = None
        for word in msg.split():
            if not word.isalpha():
                continue
                
            if prev is None:
                prev = word
                continue
            # add a new word occurence
            self.increaseWordCount(prev, word)
            prev = word