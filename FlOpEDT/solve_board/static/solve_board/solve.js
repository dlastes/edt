// This file is part of the FlOpEDT/FlOpScheduler project.
// Copyright (c) 2017
// Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public
// License along with this program. If not, see
// <http://www.gnu.org/licenses/>.
// 
// You can be released from the requirements of the license by purchasing
// a commercial license. Buying such a license is mandatory as soon as
// you develop activities involving the FlOpEDT/FlOpScheduler software
// without disclosing the source code of your own applications.

var socket;

var opti_timestamp;

var txt_area = document.getElementsByTagName("textarea")[0];

var select_opti_date, select_opti_train_prog;
var week_year_sel, train_prog_sel;

init_dropdowns();
init_constraints(constraints);

/*
function extract_week_year(){
    return {
	start:{week: +document.forms['week_form'].elements['start_week'].value,
	       year: +document.forms['week_form'].elements['start_year'].value},
	end :{week: +document.forms['week_form'].elements['end_week'].value,
	      year: +document.forms['week_form'].elements['end_year'].value},
    }
}
*/
function start() {
	console.log("GOOO");
	//var dates = extract_week_year();
	open_connection();
}

function stop() {
	console.log("STOOOOP");
	socket = new WebSocket("ws://" + window.location.host + "/solver/");
	socket.onmessage = function (e) {
		var dat = JSON.parse(e.data);
		var s = dat['message'];
		while (s.length > 0 && s.slice(-1) == '\n') {
			s = s.substring(0, s.length - 1);
		}
		if (s.length > 0) {
			txt_area.textContent += "\n" + s;
		}
	}
	socket.onopen = function () {
		socket.send(JSON.stringify({
			'message': 'kill',
			'action': "stop",
			'timestamp': opti_timestamp
		}))
	}

	socket.onclose = function (e) {
		console.error('Chat socket closed unexpectedly');
	};
	// Call onopen directly if socket is already open
	if (socket.readyState == WebSocket.OPEN) socket.onopen();
}


function format_zero(x) {
	if (x < 10) {
		return "0" + x;
	}
	return x;
}

function open_connection() {
	var now = new Date();
	opti_timestamp = now.getFullYear() + "-"
		+ format_zero(now.getMonth() + 1) + "-"
		+ format_zero(now.getDate()) + "--"
		+ format_zero(now.getHours()) + "-"
		+ format_zero(now.getMinutes()) + "-"
		+ format_zero(now.getSeconds());

	socket = new WebSocket("ws://" + window.location.host + "/solver/");
	//			  + opti_timestamp);
	socket.onmessage = function (e) {
		//	console.log(e);
		var dat = JSON.parse(e.data);
		var s = dat['message'];
		while (s.length > 0 && s.slice(-1) == '\n') {
			s = s.substring(0, s.length - 1);
		}
		if (s.length > 0) {
			txt_area.textContent += "\n" + s;
		}
	}
	socket.onopen = function () {
		// Get current training program abbrev
		var tp = '';
		if (train_prog_sel != text_all) {
			tp = train_prog_sel;
		}

		// Update constraints activation state
		update_constraints_state();

		socket.send(JSON.stringify({
			'message':
				"C'est ti-par.\n" + opti_timestamp + "\nSolver ok?",
			'action': "go",
			'department': department,
			'week': week_year_sel.week,
			'year': week_year_sel.year,
			'train_prog': tp,
			'constraints': constraints,
			'timestamp': opti_timestamp
		}))
	}

	socket.onclose = function (e) {
		console.error('Chat socket closed unexpectedly');
	};
	// Call onopen directly if socket is already open
	if (socket.readyState == WebSocket.OPEN) socket.onopen();
}

/* 
	Drop dpwn list initialization
*/

function init_dropdowns() {
	// create drop down for week selection
	select_opti_date = d3.select("#opti_date");
	select_opti_date.on("change", function () { choose_week(true); fetch_constraints();});
	select_opti_date
		.selectAll("option")
		.data(week_year_list)
		.enter()
		.append("option")
		.text(function (d) { return d['semaine']; });

	// create drop down for training programme selection
	train_prog_list.unshift(text_all);
	select_opti_train_prog = d3.select("#opti_train_prog");
	select_opti_train_prog.on("change", function () { choose_train_prog(true); fetch_constraints();});
	select_opti_train_prog
		.selectAll("option")
		.data(train_prog_list)
		.enter()
		.append("option")
		.text(function (d) { return d; });

	choose_week();
	choose_train_prog();
}

function choose_week() {
	var di = select_opti_date.property('selectedIndex');
	var sa = select_opti_date
		.selectAll("option")
		.filter(function (d, i) { return i == di; })
		.datum();
	week_year_sel = { week: sa.semaine, year: sa.an };
}
function choose_train_prog() {
	var di = select_opti_train_prog.property('selectedIndex');
	var sa = select_opti_train_prog
		.selectAll("option")
		.filter(function (d, i) { return i == di; })
		.datum();
	train_prog_sel = sa;
}

/* 
	Constraints view initialization
*/

function init_constraints(constraints) {

	// On vérifie si le navigateur prend en charge
	// l'élément HTML template en vérifiant la présence
	// de l'attribut content pour l'élément template.
	if ("content" in document.createElement("template")) {

		// On prépare une ligne pour le tableau 
		var t = document.querySelector("#constraints_template");

		// On clone la ligne et on l'insère dans le tableau
		var container = document.querySelector("#constraints");
		var current = container.firstChild;
		var target = document.createElement("div");
		container.replaceChild(target, current);

		// Create new template for each constraint
		constraints.forEach((constraint, index) => {
			var constraintId = `constraint${constraint.pk}`;

			var clone = document.importNode(t.content, true);

			var checkbox = clone.querySelector("input[type=checkbox]");
			checkbox.setAttribute('id', constraintId);
			checkbox.setAttribute('value', index);
			checkbox.checked = constraint.is_active;

			var label = clone.querySelector("label");
			label.setAttribute('for', constraintId)
			label.textContent = constraint.name;

			// display details
			for(var key in constraint.details){
				var detail = document.createElement("div")
				clone.appendChild(detail)
				
				var detail_content = document.createTextNode(`${key} : ${constraint.details[key]}`)
				detail.appendChild(detail_content)
			}

			target.appendChild(clone);
		});

	} else {
		// Une autre méthode pour ajouter les lignes
		// car l'élément HTML n'est pas pris en charge.
		alert('template element are not supported')
	}
}

/* 
	Get constraints list with updated state propepety
*/

function update_constraints_state(){
	var checkboxes = document.querySelectorAll("#constraints input[type=checkbox]");
	checkboxes.forEach(c =>{
		constraints[c.value].is_active = c.checked;
	});
}

/* 
	Get constraints async
*/

function get_constraints_url(train_prog, year, week) {

	let params = arguments;
	let regexp = /(tp)\/(1111)\/(11)/;
	let replacer = (match, train_prog, year, week, offset, string) => {
		return Object.values(params).join('/');
	}

	return fetch_constraints_url_template.replace(regexp, replacer)
}

function fetch_constraints() {
	$.ajax({
		type: "GET",
		dataType: 'json',
		url: get_constraints_url(train_prog_sel, week_year_sel.year, week_year_sel.week),
		async: true,
		contentType: "application/json; charset=utf-8",
		success: function (filtered_constraints) {
			constraints = filtered_constraints;
			init_constraints(constraints);
		 },
		error: function (msg) {
			console.log("error");
		},
		complete: function (msg) {
			console.log("complete");
		}
	});
}