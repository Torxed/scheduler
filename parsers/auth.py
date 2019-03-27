from hashlib import sha512
from os import urandom
import json

def gen_uid():
	return sha512(urandom(256)).hexdigest()

tmp = gen_uid()

class parser():
	def parse(client, data, headers, fileno, addr, *args, **kwargs):

		if set(("action","username","password")) <= data.keys():
			print('AUTH:', data)
			response = 'Failed login due to '
			if not data['username'] == 'admin':
				response += 'username and '
			if not data['password'] == 'password': # Well ware that this won't be here later :P
				response += 'password and '
			response = response[:-5]

			if data['username'] == 'admin' and data['password'] == 'password':
				token = gen_uid()
				sessions[token] = fileno
				client.send({"action" : "auth", "status" : "successful", "token" : token})
			else:
				client.send({"action" : "auth", "status" : "failed", "reason" : response})