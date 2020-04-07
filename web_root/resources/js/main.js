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
	'Planning' : {'API_CALL' : 'planning'},
	'Assignments' : {'API_CALL' : 'assignments'},
	'Projects' : {'API_CALL' : 'projects'},
}

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
					'get' : 'overview'
				}
			};
			socket.send(struct);
		})
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