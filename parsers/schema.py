from hashlib import sha512
from os import urandom, walk
import json

def gen_uid():
	return sha512(urandom(256)).hexdigest()

tmp = gen_uid()

# TODO: Replace with postgresql
schedule = {
	'administrator' : {
		2019 : {
			3 : {
				27 : [x%24 for x in range(22, 22+8)],
				28 : [x%24 for x in range(8, 16)]
			}
		}
	},
	'Anton Hvornum' : {
		2019 : {
			3 : {
				27 : [x%24 for x in range(22, 22+8)],
				28 : [x%24 for x in range(8, 16)]
			}
		}
	},
	'Someone Amazing' : {
		2019 : {
			3 : {
				27 : [x%24 for x in range(22, 22+8)],
				28 : [x%24 for x in range(8, 16)]
			}
		}
	}
}

class parser():
	def parse(client, data, headers, fileno, addr, *args, **kwargs):
		print("SCHEMA:", data)
		if set(("action", "resource", "token")) <= data.keys() and data['resource'] == 'schema' and data['action'] == 'clear':
			if data['token'] in sessions and sessions[data['token']] == fileno:
				year, month, day = [int(x) for x in data['date'].split('-')]
				if year in schedule[data['filter']] and month in schedule[data['filter']][year] and day in schedule[data['filter']][year][month]:
					del(schedule[data['filter']][year][month][day])
				client.send({**data, "status" : "success"})

		elif set(("action", "resource", "token")) <= data.keys() and data['resource'] == 'schema' and data['action'] == 'update':
			if data['token'] in sessions and sessions[data['token']] == fileno:
				year, month, day = [int(x) for x in data['date'].split('-')]
				if not year in schedule[data['filter']]:
					schedule[data['filter']][year] = {}
				if not month in schedule[data['filter']][year]:
					schedule[data['filter']][year][month] = {}

				schedule[data['filter']][year][month][day] = []
				for i in range(data['start'], data['start']+data['length']):
					if i == 24:
						day += 1
					if not year in schedule[data['filter']]:
						schedule[data['filter']][year] = {}
					if not month in schedule[data['filter']][year]:
						schedule[data['filter']][year][month] = {}
					if not day in schedule[data['filter']][year][month]:
						schedule[data['filter']][year][month][day] = []
					schedule[data['filter']][year][month][day].append((i%24))

				struct = {}
				struct[year] = {
					month : {
						day : schedule[data['filter']][year][month][day]
					}
				}
				client.send({**data, 'data' : struct})
		elif set(("action", "resource", "token")) <= data.keys() and data['resource'] == 'person' and data['action'] == 'create':
			if data['token'] in sessions and sessions[data['token']] == fileno:
				schedule[data['filter']] = {}
				client.send({**data, "status" : "success"})

		elif set(("action", "resource", "filter", "token")) <= data.keys() and data['resource'] == 'person':
			if data['token'] in sessions and sessions[data['token']] == fileno:
				results = {}
				for user in schedule:
					if data['filter'].lower() in user.lower():
						results[user] = len(schedule[user])
				client.send({**data, 'data' : results})
			else:
				client.send({**data, "status" : "failure", "reason" : "need to log in first"})

		elif set(("action", "resource", "filter", "date", "token")) <= data.keys():
			if data['resource'] == 'schema':
				if data['token'] in sessions and sessions[data['token']] == fileno:
					if data['filter'] in schedule:
						if not 'date' in data:
							client.send({**data, 'data' : schedule[data['filter']]})
						else:
							struct = {}
							year, month, day = [int(x) for x in data['date'].split('-')]
							if not year in schedule[data['filter']]:
								client.send({**data, "status" : "failure", "reason" : "No such year in planning yet."})
							elif not month in schedule[data['filter']][year]:
								client.send({**data, "status" : "failure", "reason" : "No such month in planning yet."})
							elif not day in schedule[data['filter']][year][month]:
								client.send({**data, "status" : "failure", "reason" : "No such day in planning yet."})
							else:
								struct[year] = {
									month : {
										day : schedule[data['filter']][year][month][day]
									}
								}
								client.send({**data, 'data' : struct})
					else:
						client.send({**data, "status" : "failure", "reason" : "No such user in database"})
				else:
					client.send({**data, "status" : "failure", "reason" : "need to log in first"})