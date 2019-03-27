import signal, time, importlib
from os import walk
from os.path import splitext, basename

__builtins__.__dict__['config'] = {
	'slimhttp' : {
		'web_root' : './web_content',
		'index' : 'index.html',
		'vhosts' : {
			'scheduler.se' : {
				'web_root' : './web_content',
				'index' : 'index.html'
			}
		}
	}
}

__builtins__.__dict__['LEVEL'] = 5
__builtins__.__dict__['sessions'] = {
	
}

## Import sub-modules after configuration setup.
from dependencies.slimHTTP import slimhttpd
from dependencies.spiderWeb import spiderWeb

#openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

def sig_handler(signal, frame):
	http.close()
	https.close()
	exit(0)

signal.signal(signal.SIGINT, sig_handler)

class pre_parser():
	def __init__(self, *args, **kwargs):
		self.parsers = {}

	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		## This little bundle of joy just flushes the Python cache, imports a library by string and then reloads it just in case.
		## That library is then in charge of parsing all the incoming websocket data. Meaning, no need to restart the entire server
		## if the code changes in the websocket-parser.
		importlib.invalidate_caches()
		for root, folders, files in walk('./parsers/'):
			for filename in files:
				filename = splitext(basename(filename))[0]
				if not filename in self.parsers:
					log('scheduler.se', 'core', f'Loading parser: parsers.{filename}', level=5)
					self.parsers[filename] = importlib.__import__(f'parsers.{filename}')
				log('scheduler.se', 'core', f'Reloading parser: parsers.{filename}', level=10)
				importlib.reload(self.parsers[filename])
				yield self.parsers[filename].__dict__[filename].parser.parse(client, data, headers, fileno, addr, *args, **kwargs)
			break

websocket = spiderWeb.upgrader({'default' : pre_parser()})
http = slimhttpd.http_serve(upgrades={b'websocket' : websocket})
https = slimhttpd.https_serve(upgrades={b'websocket' : websocket}, cert='cert.pem', key='key.pem')

while 1:
	for handler in [http, https]:
		client = handler.accept()

		#for fileno, client in handler.sockets.items():
		for fileno, event in handler.poll().items():
			if fileno in handler.sockets: # If not, it's a main-socket-accept and that will occur next loop
				sessions[fileno] = handler.sockets[fileno]
				client = handler.sockets[fileno]
				if client.recv():
					resposne = client.parse()
					if resposne:
						try:
							client.send(resposne)
						except BrokenPipeError:
							pass
						client.close()