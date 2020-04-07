import json, time
from hashlib import sha512

class parser():
	def process(path, client, data, headers, fileno, addr, *args, **kwargs):
		if not 'project_id' in data:
			return {
				'status' : 'success',
				'projects' : datastore['projects']
			}
		elif data['project_id'] not in datastore['projects']:
			return {
				'status' : 'failed',
				'message' : 'Project does not exist.'
			}
		else:
			return {
				'status' : 'success',
				'filtered' : True,
				'project_data' : datastore['projects'][data['project_id']]
			}
