import importlib.util, time, hashlib
import signal, json, importlib, sys, traceback
from submodules.spiderWeb import spiderWeb
from os import urandom
from os.path import isdir, isfile, split as path_split
from collections.abc import Iterator

__builtins__.__dict__['LOG_LEVEL'] = 4
__builtins__.__dict__['LOG_PRINT'] = True
__builtins__.__dict__['datastore'] = {}
__builtins__.__dict__['modules'] = {}
clients = {}

## Set up logging early on:
import logging
from systemd.journal import JournalHandler

# Custom adapter to pre-pend the 'origin' key.
# TODO: Should probably use filters: https://docs.python.org/3/howto/logging-cookbook.html#using-filters-to-impart-contextual-information
class CustomAdapter(logging.LoggerAdapter):
	def process(self, msg, kwargs):
		return '[{}] {}'.format(self.extra['origin'], msg), kwargs

logger = logging.getLogger() # __name__
journald_handler = JournalHandler()
journald_handler.setFormatter(logging.Formatter('[{levelname}] {message}', style='{'))
logger.addHandler(journald_handler)
logger.setLevel(logging.DEBUG)

def sig_handler(signal, frame):
	server.close()
	exit(0)
signal.signal(signal.SIGINT, sig_handler)

class _LOG_LEVELS:
	CRITICAL = 1
	ERROR = 2
	WARNING = 3
	INFO = 4
	DEBUG = 5
__builtins__.__dict__['LOG_LEVELS'] = _LOG_LEVELS

def _log(*msg, origin='UNKNOWN', level=5, **kwargs):
	if level <= LOG_LEVEL:
		msg = [item.decode('UTF-8', errors='backslashreplace') if type(item) == bytes else item for item in msg]
		msg = [str(item) if type(item) != str else item for item in msg]
		log_adapter = CustomAdapter(logger, {'origin': origin})
		if level <= LOG_LEVELS.CRITICAL:
			if LOG_PRINT:
				print(f'[C] {msg}')
			log_adapter.critical(' '.join(msg))
		elif level <= LOG_LEVELS.ERROR:
			if LOG_PRINT:
				print(f'[E] {msg}')
			log_adapter.error(' '.join(msg))
		elif level <= LOG_LEVELS.WARNING:
			if LOG_PRINT:
				print(f'[W] {msg}')
			log_adapter.warning(' '.join(msg))
		elif level <= LOG_LEVELS.INFO:
			if LOG_PRINT:
				print(f'[I] {msg}')
			log_adapter.info(' '.join(msg))
		else:
			if LOG_PRINT:
				print(f'[D] {msg}')
			log_adapter.debug(' '.join(msg))
__builtins__.__dict__['log'] = _log

def _gen_id(entropy_length=256):
	return hashlib.sha512(urandom(entropy_length)).hexdigest()
__builtins__.__dict__['gen_id'] = _gen_id


def _uid(seed=None, bits=32):
	if not seed:
		seed = urandom(bits) + bytes(str(time.time()), 'UTF-8')
	return hashlib.sha512(seed).hexdigest().upper()
__builtins__.__dict__['uid'] = _uid


def _short_uid(seed=None, bits=32):
	if not seed:
		seed = urandom(bits) + bytes(str(time.time()), 'UTF-8')
	return hashlib.sha1(seed).hexdigest().upper()
__builtins__.__dict__['short_uid'] = _short_uid


def find_final_module_path(path, data):
	if '_module' in data:
		if data['_module'] in data and '_module' in data[data['_module']] and isdir(f"{path}/{data['_module']}"):
			return find_final_module_path(path=f"{path}/{data['_module']}", data=data[data['_module']])
		elif isfile(f"{path}/{data['_module']}.py"):
			return {'path' : f"{path}/{data['_module']}.py", 'data' : data, 'api_path' : ':'.join(f"{path}/{data['_module']}"[len('./api_modules/'):].split('/'))}

def importer(path):
	old_version = False
	log(f'Request to import "{path}"', level=6, origin='importer')
	if path not in modules:
		## https://justus.science/blog/2015/04/19/sys.modules-is-dangerous.html
		try:
			log(f'Loading API module: {path}', level=4, origin='importer')
			#importlib.machinery.SOURCE_SUFFIXES.append('') # empty string to allow any file
			spec = importlib.util.spec_from_file_location(path, path)
			modules[path] = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(modules[path])
			#sys.modules[path[:-3]] = modules[path]
			sys.modules[path] = modules[path]
			# if desired: importlib.machinery.SOURCE_SUFFIXES.pop()
			#modules[path] = importlib.import_module(path, path)
		except (SyntaxError, ModuleNotFoundError) as e:
			log(f'Failed to load API module ({e}): {path}', level=2, origin='importer')
			return None
	else:
		#log(f'Reloading API module: {path}', level=4, origin='importer')
		#for key in sys.modules:
		#	print(key, '=', sys.modules[key])
		try:
			raise SyntaxError('https://github.com/Torxed/ADderall/issues/11')
			## Important: these two are crucial elements
			#importlib.invalidate_caches()

			#print('Reloading:', modules[path])
			#importlib.reload(modules[path])
		except SyntaxError as e:
			old_version = True
			#log(f'Failed to reload API module ({e}): {path}', level=2, origin='importer')
	return old_version, modules[f'{path}']

class parser():
	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		#print('Input:', json.dumps(data, indent=4))

		## This little bundle of joy, imports python-modules based on what module is requested from the client.
		## If the reload has already been loaded once before, we'll invalidate the python module cache and
		## reload the same module so that if the code has changed on disk, it will now be executed with the new code.
		##
		## This prevents us from having to restart the server every time a API endpoint has changed.

		# If the data isn't JSON (dict)
		# And the data doesn't contain _module, !abort!
		if type(data) is not dict or '_module' not in data:
			log(f'Invalid request sent, missing _module or _id in JSON data: {str(data)[:200]}', level=3, origin='pre_parser', function='parse')
			return


		## TODO: Add path security!
		module_to_load = find_final_module_path('./api_modules', data)
		if(module_to_load):
			import_result = importer(module_to_load['path'])
			if import_result:
				old_version, handle = import_result

				# Just keep track if we're executing the new code or the old, for logging purposes only
				if not old_version:
					log(f'Calling {handle}.parser.process(client, data, headers, fileno, addr, *args, **kwargs)', level=4, origin='pre_parser', function='parse')
				else:
					log(f'Calling old {handle}.parser.process(client, data, headers, fileno, addr, *args, **kwargs)', level=3, origin='pre_parser', function='parse')

				try:
					response = modules[module_to_load['path']].parser.process(f'api_modules', client, module_to_load['data'], headers, fileno, addr, *args, **kwargs)
					if response:
						if isinstance(response, Iterator):
							for item in response:
								yield {
									**item,
									'_uid' : data['_uid'] if '_uid' in data else None,
									'_modules' : module_to_load['api_path']
								}
						else:
							yield {
								**response,
								'_uid' : data['_uid'] if '_uid' in data else None,
								'_modules' : module_to_load['api_path']
							}
				except BaseException as e:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = path_split(exc_tb.tb_frame.f_code.co_filename)[1]
					log(f'Module error in {fname}@{exc_tb.tb_lineno}: {e} ', level=2, origin='pre_parser', function='parse')
					log(traceback.format_exc(), level=2, origin='pre_parser', function='parse')
		else:
			log(f'Invalid data, trying to load a inexisting module: {data["_module"]} ({str(data)[:200]})', level=3, origin='pre_parser', function='parse')	

server = spiderWeb.server({'default' : parser()}, address='', port=3334)