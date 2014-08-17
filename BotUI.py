
import web
import threading
import webbrowser
import json

from json import JSONEncoder

def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = JSONEncoder().default # save unmodified default
JSONEncoder.default = _default # replacement
        
urls = (
    '/', 'hello',
    '/game', 'game'
)

global_bot = None

class hello:        
    def GET(self):
    	raise web.seeother('/static/index.html')

class game:
    def GET(self):
    	global global_bot
        if(global_bot is not None):
        	return json.dumps(dict(game=global_bot.game, heur=global_bot.heur))
        else:
        	return json.dumps(dict())


class BotUIServer(web.application):
	def run(self	, port=8080, *middleware):
		func = self.wsgifunc(*middleware)
		self.server = web.httpserver.runsimple(func, ('localhost', 8080))
		self.server.start()

	def stop(self):
		self.server.stop()


class BotUI(threading.Thread):
	
	def setBot(self, bot):
		global global_bot
		global_bot = bot

	def run(self):
		print "Running BotUI Thread..."
		self.bot_ui = BotUIServer(urls, globals())
		self.bot_ui.run()

	def open(self):
		new = 2
		url = "http://localhost:8080"
		webbrowser.open(url,new=new)

	def stop(self):
		self.bot_ui.stop()