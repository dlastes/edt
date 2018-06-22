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

var socket ;

var opti_timestamp ;

function extract_week_year(){
    return {
	start:{week: +document.forms['week_form'].elements['start_week'].value,
	       year: +document.forms['week_form'].elements['start_year'].value},
	end :{week: +document.forms['week_form'].elements['end_week'].value,
	      year: +document.forms['week_form'].elements['end_year'].value},
    }
}

function start(){
    console.log("GOOO");
    var dates = extract_week_year();
    open_connection(dates);
}
function stop(){
    console.log("STOOOOP");
    var dates = extract_week_year();
}


function format_zero(x) {
    if ( x < 10 ) {
	return "0" + x ;
    }
    return x ;
}


function open_connection(date){
    var now = new Date();
    opti_timestamp = now.getFullYear() + "-"
	+ format_zero(now.getMonth() + 1) + "-"
	+ format_zero(now.getDate()) + "--"
	+ format_zero(now.getHours()) + "-"
	+ format_zero(now.getMinutes()) + "-"
	+ format_zero(now.getSeconds()) ;
    
    socket = new WebSocket("ws://" + window.location.host + "/solver/"
			  + opti_timestamp);
    socket.onmessage = function(e) {
	var txt_area = document.getElementsByTagName("textarea")[0];
	txt_area.textContent += "\n" + e.data ;
    }
    socket.onopen = function() {
	socket.send("C'est ti-par.\n"+opti_timestamp+"\nSolver ok?");
    }

    // Call onopen directly if socket is already open
    if (socket.readyState == WebSocket.OPEN) socket.onopen();

    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_run + opti_timestamp + "?sw=" + date.start.week
	    + "&sy=" + date.start.year
	    + "&ew=" + date.end.week
	    + "&ey=" + date.end.year,
        async: true,
        contentType: "text/json",
        success: function(msg) {
            console.log(msg);
	    var rec = JSON.parse(msg) ;
	    if (rec['text'] != 'ok') {
		socket.send(rec['text']) ;
	    }
        },
        error: function(msg) {
            console.log("error");
        }
    });


}
