#!/usr/bin/python
# uniquebot - by dcchut
# based on skeleton code by Twisted Matrix Laboratories 

# twisted imports
from twisted.internet import reactor
from twisted.python import log
from uniquebot import Uniquebot, UniqueBotFactory

# system imports
import sys
from daemon import Daemon

# make sure only unique things are said
class UBDaemon(Daemon):
	def run(self):
		# initialize logging
		log.startLogging(sys.stdout)
		
		# create factory protocol and application
		f = UniqueBotFactory(self.password, self.channel, self.dbfile)

		# connect factory to this host and port
		reactor.connectTCP(self.server, self.port, f)
		
		# run bot
		reactor.run()

if __name__ == '__main__':
	daemon = UBDaemon("/tmp/ubdaemon.pid')
	
	if len(sys.argv) == 6:
		if 'start' == sys.argv[1]:
			daemon.password = sys.argv[5]
			daemon.channel = sys.argv[3]
			daemon.dbfile = sys.argv[4]
			daemon.server = sys.argv[2]
			daemon.port = 6667
			daemon.start()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	elif len(sys.argv) == 2:
		if 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart [<server[:port]> <channel> <dbfile> <password>" % sys.argv[0]
		sys.exit(2)
		
	
	# give me the password!
	if len(sys.argv) != 5:
		print "Usage: uniquebot.py <server[:port]> <channel> <dbfile> <password>\n"
		sys.exit(1)
