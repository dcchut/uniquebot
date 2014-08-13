#!/usr/bin/python
# uniquebot - by dcc

import os, sys, yaml

from uniquebot.core.bot import UniqueBotFactory
from twisted.internet import reactor
from twisted.python import log

if __name__ == '__main__':
	if len(sys.argv) != 6:
		print "Usage: main.py <server[:port]> <channel> <dbfile> <password> <nickname>\n"
		sys.exit(1)
		
	# split server in server & port
	c = sys.argv[1].split(':')
	
	if len(c) == 1:
		port = 6667
	else:
		port = c[1]
	
	# load the config file
	cfg = yaml.load(file('config.cfg'))
	
	# register all of the plugins
	plugin_dir = os.listdir('uniquebot/plugins')
	plugins    = {}

	for plugin in plugin_dir:
		# get the "name" of the plugin
		plugin_name   = "".join(plugin.split(".")[0:-1])
		plugin_module = "uniquebot.plugins.%s" % plugin_name

		if plugin_name == '__init__' or plugin_name in plugins or plugin_name in cfg['disabled_plugins']:
			continue
		
		# import the shit out of it
		plugin_internal_name = '__plugin_magic_{0}'.format(plugin_name)
		exec("import {0} as {1}".format(plugin_module, plugin_internal_name))
		
		# now grab an instance of the plugin
		plugins[plugin_name] = globals()[plugin_internal_name].Plugin(plugin_name, plugin_internal_name, plugin_module)

	log.startLogging(sys.stdout)

	# create factory
	f = UniqueBotFactory(sys.argv[5], sys.argv[4], sys.argv[2], sys.argv[3], plugins, cfg)
	reactor.connectTCP(c[0], port, f)
	reactor.run()
