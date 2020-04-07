import json, time
from hashlib import sha512
from collections import OrderedDict

datastore['customers'] = OrderedDict({
	gen_id() : {
		'displayname' : 'Test AB',
		'projects' : {
			gen_id() : True
		}
	},
	gen_id() : {
		'displayname' : 'Evil Scientist AB',
		'projects' : {
			gen_id() : True
		}
	},
	gen_id() : {
		'displayname' : 'Example HB',
		'projects' : {
			gen_id() : True
		}
	}
})

_ = list(datastore['customers'].keys())
datastore['projects'] = OrderedDict({
	list(datastore['customers'][_[0]]['projects'].keys())[0] : {
		'displayname' : 'Test 1',
		'customer' : list(datastore['customers'].keys())[0],
		'start' : '2020-04-14 10:00',
		'end' : '2020-05-02 17:00',
		'seller' : None,
		'customer_poc' : None,
		'due_date' : None,
		'assigned' : {},
		'files' : {},
		'owner' : None
	},
	list(datastore['customers'][_[2]]['projects'].keys())[0] : {
		'displayname' : 'Test 3',
		'customer' : list(datastore['customers'].keys())[2],
		'customer' : 'AB Test AB',
		'start' : '2020-04-14 10:00',
		'end' : '2020-04-17 17:00',
		'seller' : None,
		'customer_poc' : None,
		'due_date' : None,
		'assigned' : {},
		'files' : {},
		'owner' : None
	},
	list(datastore['customers'][_[1]]['projects'].keys())[0] : {
		'displayname' : 'Test 2',
		'customer' : list(datastore['customers'].keys())[1],
		'customer' : 'Tset  AB',
		'start' : '2020-04-20 10:00',
		'end' : '2020-04-24 17:00',
		'seller' : None,
		'customer_poc' : None,
		'due_date' : None,
		'assigned' : {},
		'files' : {},
		'owner' : None
	}
})

html = """
<div class="projectArea">
	<div class="customers">

	</div>
	<div class="projectlist">

	</div>
	<div class="projectInfo">
	</div>
</div>
"""

script = """
console.log("moo");
"""

class parser():
	def process(path, client, data, headers, fileno, addr, *args, **kwargs):
		return {
			'status' : 'success',
			'html' : {
				'content' : html,
				'target' : '.main_area',
				'replace' : True
			},
			'javascript' : None
		}

