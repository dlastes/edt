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


var logo = {scale: .07,
	    init:{dim: 1000,
		  margin: 50,
		  width_fl: .9,
		  width_op: 1.35,
		  width_edt: 2.3,
		  fontsize_main: 600,
		  fontsize_hline: 150},
	    get_current_dim: function () {
		return this.scale * this.init.dim ;},
	    get_current_margin: function () {
		return this.scale * this.init.margin ;},
	    get_current_fs_main: function () {
		return this.scale * this.init.fontsize_main ;},
	    get_current_fs_hline: function () {
		return this.scale * this.init.fontsize_hline ;},
	    get_current_width_fl: function () {
		return this.scale * this.init.fontsize_main * this.init.width_fl ;},
	    get_current_width_op: function () {
		return this.scale * this.init.fontsize_main * this.init.width_op ;},
	    get_current_width_edt: function () {
		return this.scale * this.init.fontsize_main * this.init.width_edt ;},
	   };


init_logo();
add_text();
    console.log(logo.svg.attr("width"));


function add_text() {

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
    
    
    logo.svg = d3
	.select("#live-logo")
	.select("svg");


    logo.svg
	.select("#dims")
	.attr("transform", "scale(" + logo.scale + ")");

    var txt_gp = logo.svg
	.append("g")
	.attr("class","main");

    var style = "alignment-baseline: hanging;"
	+ "font-family: 'flog'; ";
    var style_fs_main = "font-size: " + logo.get_current_fs_main() + "px;";
    var style_fs_hline = "font-size: " + logo.get_current_fs_hline() + "px;";
    
    var current_main_x = logo.get_current_dim()+logo.get_current_margin();
    var main_y = logo.get_current_margin() ;
    
    txt_gp
	.append("text")
	.attr("x",current_main_x)
	.attr("y", main_y)
	.attr("style", style + style_fs_main)
	.text("Fl")
	.style('fill', 'black');

    current_main_x += logo.get_current_width_fl() ;
    txt_gp
	.append("text")
	.attr("x",current_main_x)
	.attr("y",main_y)
	.attr("style", style + style_fs_main)
	.text("Op")
	.style('fill', 'red');

    current_main_x += logo.get_current_width_op() ;
    txt_gp
	.append("text")
	.attr("x",current_main_x)
	.attr("y",main_y)
	.attr("style", style + style_fs_main)
	.text("EDT")
	.style('fill', 'black');

    current_main_x += logo.get_current_width_edt() ;
    logo.svg
	.attr("width", current_main_x)
	.attr("height", logo.get_current_dim() + logo.get_current_margin());


    style = "alignment-baseline: hanging;"
	+ "font-family: 'Verdana'; font-size: 10px";

    txt_gp = logo.svg
	.append("g")
	.attr("class","headline");

    txt_gp
	.append("text")
	.text("Créateur d'emploi du temps")
	.attr("x", logo.get_current_dim()+logo.get_current_margin())
	.attr("y", .7*logo.get_current_dim())
	.attr("style", style)
	.attr("fill", '#555');
    
    txt_gp
	.append("text")
	.text("Flexible et OpenSource")
	.attr("x", logo.get_current_dim()+logo.get_current_margin())
	.attr("y", .89*logo.get_current_dim())
	.attr("style", style)
	.attr("fill", '#555');

//    style += " text-anchor:end;"

    txt_gp
	.append("text")
	.text("AGPL v.3")
	.attr("x", +logo.svg.attr("width") - logo.get_current_margin())
	.attr("y", .89*logo.get_current_dim())
	.attr("style", style)
	.attr("text-anchor", "end")
	.attr("fill", '#555');
    
    
}

function init_logo() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url_logo, false);
    xhr.overrideMimeType("image/svg+xml");
    xhr.send("");
    var lolo = document.getElementById("live-logo");
    lolo.appendChild(xhr.responseXML.documentElement);
    var d = new Date();
    var hm = new Array(2);
    hm[0] = 360*(d.getHours() % 12 + d.getMinutes()/60)/12;
    hm[1] = 360*(d.getMinutes()+d.getSeconds()/60)/60;
    console.log(hm);
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


//      <div id="image">
       
//        <div id="live-logo">
//        </div>
//        <div id="texteImage"> 
	 
// 	 <span id="txtFlop"> 
// 	   Fl<span id=opRed >Op</span>EDT<br> 
// 	 </span>
	 
// 	 <div id="texteSous">
	   
// 	   {% autoescape off %}
// 	   <span id="txtFlop2">
// 	     {{ image }}
// 	   </span>
// 	   {% endautoescape %}
	   
// 	   <span id="agpl">
// 	     AGPL v.3
// 	   </span>
// 	 </div>
//        </div>
// </div>
// <script>
// </script>  

// </a>
