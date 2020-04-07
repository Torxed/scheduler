dummy_weeks = {
}
for(let i=1; i<=52; i++) {
	dummy_weeks[i] = {}
}
dummy_people = {
	"1" : {
		"displayname" : "Anton Hvornum",
		"assignments" : {
			"2" : {
				"0" : {"assignment" : 1},
				"1" : {"assignment" : 1},
				"2" : {"assignment" : 1},
				"3" : {"assignment" : 1},
				"4" : {"assignment" : 1}
			},
			"3" : {
				"0" : {"assignment" : 1},
				"1" : {"assignment" : 1},
				"2" : {"assignment" : 1},
				"3" : {"assignment" : 0}
			}
		}
	},
	"2" : {
		"displayname" : "Anton Hvornum 2",
		"assignments" : {
			"2" : {
				"0" : {"assignment" : 2},
				"1" : {"assignment" : 2},
				"2" : {"assignment" : 2},
				"3" : {"assignment" : 2},
				"4" : {"assignment" : 2}
			},
			"3" : {
				"0" : {"assignment" : 2},
				"1" : {"assignment" : 2},
				"2" : {"assignment" : 2},
				"3" : {"assignment" : 2},
				"4" : {"assignment" : 2}
			},
			"4" : {
				"0" : {"assignment" : 0},
				"1" : {"assignment" : 0},
			}
		}
	},
	"3" : {
		"displayname" : "Anton Hvornum 3",
		"assignments" : {
			"2" : {
				"0" : {"assignment" : 2},
				"1" : {"assignment" : 2},
				"2" : {"assignment" : 2},
				"3" : {"assignment" : 2},
				"4" : {"assignment" : 2}
			},
			"3" : {
				"0" : {"assignment" : 2},
				"1" : {"assignment" : 2},
				"2" : {"assignment" : 2},
				"3" : {"assignment" : 2},
				"4" : {"assignment" : 2}
			},
			"4" : {
				"0" : {"assignment" : 0},
				"1" : {"assignment" : 0},
			}
		}
	},
	"4" : {
		"displayname" : "Anton Hvornum 4",
		"assignments" : {
			"2" : {
				"0" : {"assignment" : 1},
				"1" : {"assignment" : 1},
				"2" : {"assignment" : 1},
				"3" : {"assignment" : 1},
				"4" : {"assignment" : 1}
			},
			"3" : {
				"0" : {"assignment" : 1},
				"1" : {"assignment" : 1},
				"2" : {"assignment" : 1},
				"3" : {"assignment" : 0}
			}
		}
	}
}

menu = {
	'Planning' : {'API_CALL' : 'planning', 'function' : planning_overview},
	'Assignments' : {'API_CALL' : 'assignments', 'function' : assignments_overview},
	'Projects' : {'API_CALL' : 'projects', 'function' : projects_overview},
}

timers = {};
customers_cache = {};
projects_cache = {};

function append_stats_to_html_obj(obj, stats) {
	if (typeof stats === 'undefined')
		return;

	Object.keys(stats).forEach((key) => {
		if (key == 'id')
			obj.id = stats.id;
		else if (key == 'classList')
			obj.classList = stats.classList;
		else if (key == 'innerHTML')
			if (typeof stats['innerHTML'] == 'object') {
				obj.appendChild(stats['innerHTML'])
			} else {
				obj.innerHTML = stats['innerHTML'];
			}
		else
			obj.setAttribute(key, stats[key])
	})

}

function create_html_obj(type, stats, parent) {
	let obj = document.createElement(type);
	append_stats_to_html_obj(obj, stats);

	if (parent)
		parent.appendChild(obj);

	return obj
}

function has_assignment_this_day(userinfo, week, day) {
	if(typeof userinfo['assignments'][week] === 'undefined')
		return false;
	else if(typeof userinfo['assignments'][week][day] === 'undefined')
		return false;
	return true;
}

function load_menu() {
	let menu_obj = document.querySelector('.menu_buttons');

	for (let [title, api_info] of Object.entries(menu)) {
		let menu_item = create_html_obj('li', {'innerHTML' : title}, menu_obj);

		menu_item.addEventListener('click', () => {
			let struct = {
				'_module' : api_info['API_CALL'],
				[api_info['API_CALL']] : {
					'_module' : 'overview'
				}
			};
			socket.send(struct);
		})

		socket.subscribe(api_info['API_CALL']+':overview', api_info['function']);
	}
}

function load_users() {
	let names_o = document.querySelector('.names');

	for (let [people_id_str, people_info] of Object.entries(dummy_people)) {
		let nameplate = create_html_obj('div', {'classList' : 'name', 'userid' : people_id_str, 'innerHTML' : people_info['displayname']}, names_o);
	}
}

function load_weeks() {
	let weeks_o = document.querySelector('.weeks');

	for (let [week_nr_str, week_info] of Object.entries(dummy_weeks)) {
		let week_nr = parseInt(week_nr_str);
		let week_o = create_html_obj('div', {'classList' : 'week', 'week' : week_nr}, weeks_o);
		let week_heading = create_html_obj('div', {'classList' : 'person week_header', 'innerHTML' : week_nr}, week_o);

		week_o.addEventListener('mouseenter', (event) => {
			week_o.classList.toggle('mouse_over')
		})
		week_o.addEventListener('mouseleave', (event) => {
			week_o.classList.toggle('mouse_over')
		})

		for (let [userid_str, userinfo] of Object.entries(dummy_people)) {
			let userid = parseInt(userid_str);

			let person_weekobj = create_html_obj('div', {'classList' : 'person', 'userid' : userid}, week_o);
			for(let day=0; day < 5; day++) {
				let person_dayobj = null;
				if(has_assignment_this_day(userinfo, week_nr, day)) {
					switch(userinfo['assignments'][week_nr][day]['assignment']) {
						case 0:
							person_dayobj = create_html_obj('div', {'classList' : 'day relax', 'userid' : userid, 'week' : week_nr}, person_weekobj);
							break;
						case 1:
							person_dayobj = create_html_obj('div', {'classList' : 'day booked', 'userid' : userid, 'week' : week_nr}, person_weekobj);
							break;
						case 2:
							person_dayobj = create_html_obj('div', {'classList' : 'day booked', 'userid' : userid, 'week' : week_nr}, person_weekobj);
							break;
					}
				} else {
					person_dayobj = create_html_obj('div', {'classList' : 'day', 'userid' : userid, 'week' : week_nr}, person_weekobj);
				}
			}
		}
	}
}

function genericPageLoader(data) {
	if(typeof data['html'] !== 'undefined') {
		let target = document.querySelector('.main_area');
		if(typeof data['html']['target'] !== 'undefined')
			target = document.querySelector(data['html']['target']);

		target.innerHTML = data['html']['content'];
	}

	if(typeof data['javascript'] !== 'undefined' && data['javascript']) {
		let script = document.querySelector('#script_'+data['_modules']);
		if(script)
			script.remove();

		script = document.createElement('script');
		script.id = 'script_'+data['_modules'];
		script.innerHTML = data['javascript'];
		document.head.appendChild(script);
	}

	return true;
}

function handle_message(json) {
	
}

function planning_overview(json) {

}
function assignments_overview(json) {
	
}
function projects_overview(json) {
	if(json['status'] == 'success') {
		console.log('Rendering overview');
		let struct = null;
		genericPageLoader(json);


		struct = {
			'_module' : 'customers',
			'customers' : {
				'_module' : 'getAll'
			}
		}
		socket.subscribe('customers:getAll', (data) => {
			let customers = document.querySelector('.customers');
			for (let [customer_id_str, customer_info] of Object.entries(data['customers'])) {
				let customer_button = create_html_obj('div', {'classList' : 'customerbutton', 'innerHTML' : customer_info['displayname']}, customers);
				customers_cache[customer_id_str] = customer_info;
			}
		});
		socket.send(struct)

		struct = {
			'_module' : 'projects',
			'projects' : {
				'_module' : 'getAll'
			}
		}
		socket.subscribe('projects:getAll', (data) => {
			if(typeof data['filtered'] === 'undefined' || !data['filtered']) {
				let projects = document.querySelector('.projectlist');
				for (let [project_id_str, project_info] of Object.entries(data['projects'])) {
					let project_button = create_html_obj('div', {'classList' : 'customerbutton', 'innerHTML' : project_info['displayname'] + ' (' + project_info['start'] + ')'}, projects);
					project_button.addEventListener('click', () => {
						view_project(project_id_str, '.projectInfo');
					})
				}
			}
		});
		socket.send(struct)

		/*
		let projectlist = document.querySelector('.projectlist');
		let customers = {};
		for (let [project_id_str, project_info] of Object.entries(json['projects'])) {
			if(typeof customers[project_info['customer']] === 'undefined') {
				let customer_button = create_html_obj('div', {'classList' : 'customerbutton', 'innerHTML' : project_info['customer']}, projectlist);
				customers[project_info['customer']] = true;
			}
		}
		*/

		return true;
	} else {
		console.error('Could not handle projects overview:', json);
		return false;
	}
}

function view_project(project_id, container) {
	let struct = {
		'_module' : 'projects',
		'projects' : {
			'_module' : 'getAll',
			'project_id' : project_id
		}
	}
	socket.subscribe('projects:getAll', (data) => {
		let container_o = document.querySelector(container);
		console.log(container, container_o);
		
		console.log(customers_cache);
		let customer = create_html_obj('p', {'classList' : 'customerInfoGeneral customer', 'innerHTML' : customers_cache[data['project_data']['customer']]['displayname']}, container_o);
		let displayname = create_html_obj('p', {'classList' : 'customerInfoGeneral displayname', 'innerHTML' : data['project_data']['displayname']}, container_o);

		let start = create_html_obj('p', {'classList' : 'customerInfoGeneral startdate', 'innerHTML' : data['project_data']['start']}, container_o);
		let end = create_html_obj('p', {'classList' : 'customerInfoGeneral enddate', 'innerHTML' : data['project_data']['end']}, container_o);

		let seller = null;
		if(data['project_data']['seller'])
			seller = create_html_obj('p', {'classList' : 'customerInfoGeneral seller', 'innerHTML' : data['project_data']['seller']}, container_o);
		else
			seller = create_html_obj('p', {'classList' : 'customerInfoGeneral seller', 'innerHTML' : 'Unknown'}, container_o);

		return true;
	});
	socket.send(struct)
}