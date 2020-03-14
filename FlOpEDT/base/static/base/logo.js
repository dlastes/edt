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








    /*
     +----------------------------------------------------+
     |			^				  |
     |			| 50                              |
     |			v				  |
     |       +---------------+  +---------------+	  |
     |       |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |<----->+---------------+  +---------------+	  |
     |  50   |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |       +---------------+  +---------------+	  |
     |       |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |                       1050                         |
     |<-------------------------------------------------->|
     +----------------------------------------------------+       
     */

var logo = {scale: .12,
	    init:{dim: 1000,
		  margin: 50},
	    get_current_dim: function () {
		return this.scale * this.init.dim ;},
	    get_current_margin: function () {
		return this.scale * this.init.margin ;}
	   }


var headlines =
    [ "Gestionnaire d'emploi du temps <span id=\"flopGreen\">fl"
        + "</span>exible et <span id=\"flopGreen\">op</span>enSource",
      "\"Qui veut faire les <span id=\"flopRed\">EDT</span> cette année ?\" ... "
      + "<span id=\"flopGreen\">flop</span> !",
      "Et votre emploi du temps fera un "
      + "<span id=\"flopRedDel\">flop</span> carton !",
      "Et même votre logo sera à l'heure..." 
    ];


init_logo();


function init_logo() {
    fetch_logo();
    init_date();
    resize_logo();
    add_headline();
}


// fetch the logo and include it as svg
function fetch_logo(){
    var xhr = new XMLHttpRequest();
    xhr.open("GET",url_logo,false);
    xhr.overrideMimeType("image/svg+xml");
    xhr.send("");
    var lolo = document.getElementById("live-logo");
    lolo.appendChild(xhr.responseXML.documentElement);
}


// initialize the long and short hands of the logo
function init_date() {
    var d = new Date();
    var hm = new Array(2);
    hm[0] = 360*(d.getHours() % 12 + d.getMinutes()/60)/12;
    hm[1] = 360*(d.getMinutes()+d.getSeconds()/60)/60;
    var anim = new Array(2);
    anim[0] = document.getElementById("csh")
	.getElementsByTagName("animateTransform")[0];
    anim[1] = document.getElementById("clh")
	.getElementsByTagName("animateTransform")[0];
    for (var i = 0 ; i<2 ; i++) {
	var from = anim[i].getAttribute("from").split(" ");
	from[0] = (+from[0]) + hm[i] ;
	anim[i].setAttribute("from", from.join(" "));
	var to = anim[i].getAttribute("to").split(" ");
	to[0] = (+to[0]) + hm[i] ;
	anim[i].setAttribute("to", to.join(" "));
    }
}


function resize_logo() {
    logo.svg = d3
	.select("#live-logo")
	.select("svg");
  
  
    logo.svg
	.select("#dims")
	.attr("transform", "scale(" + logo.scale + ")");
  
    logo.svg
	.attr("width", logo.get_current_dim() + logo.get_current_margin())
	.attr("height", logo.get_current_dim() + logo.get_current_margin());
}

function add_headline() {
    var draw = Math.floor(Math.random()*headlines.length);
    document.getElementById("head_logo").innerHTML = headlines[draw];
}


// helper functions to manipulate rotations in the DOM
function get_rotate_array(id) {
    var ret = document.getElementById(id).getAttribute("transform").slice(7,-1).split(" ");
    return ret.map(function(d){ return +d; });
}
function set_rotate(id, array) {
    document.getElementById(id).setAttribute("transform",
                                             "rotate("+array.join(" ")+")");
}


// drag long hand
function logo_transform() {


    // compute new angle for the long hand
    
    var init_rotation = d3.select("#clh animateTransform").attr("from_init").split(" ");
    var old_rotation = get_rotate_array("clh");
    var new_rotation = init_rotation.slice();
    
    var center = {x:init_rotation[1], y:init_rotation[2]} ;//document.getElementById("longh_rotate").getBoundingClientRect();
    var mouse = {x: d3.event.x, y: d3.event.y} ;
    var dx = center.x - mouse.x ;
    var dy = center.y - mouse.y ;

    var angle = 180*Math.atan(Math.abs(dx)/Math.abs(dy))/Math.PI;
    if(dx>0) {
        if(dy>0) {
            angle = 360-angle ;
        } else {
            angle = 180+angle ;
        }
    } else {
        if(dy<0) {
            angle = 180-angle ;
        } else {
            angle = 360 + angle ;
        }
    }
    
    new_rotation[0] = (+init_rotation[0] + angle) % 360 ;

    set_rotate("clh", new_rotation);


    // set the short hand accordingly
    old_rotation[0] = +old_rotation[0] % 360 ;
    var diff = (new_rotation[0] - old_rotation[0] + 360) % 360 ;

    if (diff >= 180) {
        diff -= 360 ;
    }

    var rotation = get_rotate_array("csh") ;

    diff = diff/12 ;

    rotation[0] = +rotation[0] + diff ;
    set_rotate("csh", rotation);
}

// disable animation
function drag_hand_start() {
    ['#clh', '#csh'].forEach( function(hand) {
        console.log(hand);
        var bu = d3.select(hand).attr("transform");
        d3.select(hand + " animateTransform").attr("attributeName", "transformBU");
        d3.select(hand).attr("transform",bu);
    } );
}

// re-enable animation and check final hour
function drag_hand_end() {
    var stop = ['clh', 'csh'].map( function(hand) {
        var current = get_rotate_array(hand) ;
        d3.select("#" + hand + " animateTransform").attr("from", current.join(" "));
        current[0] += 360 ;
        d3.select("#" + hand + " animateTransform").attr("to", current.join(" "));
        d3.select("#" + hand + " animateTransform").attr("attributeName", "transform");
        var init_rotation = d3.select("#" + hand + " animateTransform").attr("from_init").split(" ");
        init_rotation[0] = init_rotation[0] % 360 ;
        return (current[0] - init_rotation[0] + 360)%360 ;
    } );

    var accuracy = 10 ;

    if (Math.abs(stop[0] % 360) < accuracy && Math.abs(stop[1] - 10*360/12) < accuracy) {
        document.location.href = url_game;
    }
}

// enable drag on the long hand
var logo_listener = d3.drag()
    .on('start', drag_hand_start)
    .on('drag', logo_transform)
    .on('end', drag_hand_end);

d3.select("#clh").call(logo_listener);

