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


// Redefinition of some variables

var margin = {top: 50,  left: 100, right: 10, bot:10};

var svg = {height: 625 - margin.top - margin.bot, width: 680 - margin.left - margin.right};

// check ack -> ack.edt ?

smiley.tete = 13 ;

var data_grid_scale_day = ["LUNDI","MARDI","MERCREDI","JEUDI","VENDREDI"];

dim_dispo.width  = 80 ;
dim_dispo.height = 500 ;
dim_dispo.mh = 10 ;
dim_dispo.plot = 1 ;
nbRows=1;
scale = dim_dispo.height / nb_minutes_in_grid()  ;


ckbox["dis-mod"].cked = true ;

pref_only = true ;





create_general_svg_pref_only();
create_dh_keys();
create_lunchbar();
fetch_pref_only();





function create_lunchbar() {
    fg
	.append("line")
	.attr("class","lunchbar")
	.attr("stroke","black")
	.attr("stroke-width",6)
	.attr("x1",0)
	.attr("y1",gsclb_y)
	.attr("x2",gsclb_x)
	.attr("y2",gsclb_y);

}

function create_general_svg_pref_only() {
    svg_cont = d3.select("body").select("[id=\"svg\"]").append("svg")
	.attr("width",svg.width)
	.attr("height",svg.height)
	.attr("text-anchor","middle")
	.append("g")
	.attr("transform","translate("+margin.left + "," + margin.top + ")");

    create_layouts_pref_only(svg_cont);
}


function create_layouts_pref_only(svg_cont){


    // valider
    vg = svg_cont.append("g")
	.attr("id","lay-vg");
    
    // background, middleground, foreground, dragground
    var edtg = svg_cont.append("g")
        .attr("id", "lay-edtg");
    bg = edtg.append("g")
        .attr("id", "lay-bg");
    mg = edtg.append("g")
        .attr("id", "lay-mg");
    // fig = edtg.append("g")
    //     .attr("id", "lay-fig");
    fg = edtg.append("g")
        .attr("id", "lay-fg");

    // context menus ground
    var cmg = svg_cont.append("g")
        .attr("id", "lay-cmg");
    cmpg = cmg.append("g")
	.attr("id", "lay-cmpg");
    cmtg = cmg.append("g")
	.attr("id", "lay-cmtg");
    
    // drag ground
    dg = svg_cont.append("g")
        .attr("id", "lay-dg");

    
}


/*---------------------
  ------- DISPOS ------
  ---------------------*/
function fetch_pref_only() {
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_fetch_stype ,
        async: false,
        contentType: "text/csv",
        success: function (msg) {
	    console.log(msg);
	    
	    console.log("in");

	    user.dispos_type = [] ;
	    user.dispos_type = d3.csvParse(msg, translate_dispos_from_csv);
	    create_dispos_user_data();
	    fetch.dispos_ok = true ;
	    go_pref(true);
            show_loader(false);
	    
        },
	error: function(xhr, error) {
	    console.log("error");
	    console.log(xhr);
	    console.log(error);
	    console.log(xhr.responseText);
            show_loader(false);
	    // window.location.href = url_login;
	    //window.location.replace(url_login+"?next="+url_stype);
	}
    });
}


















function dispo_x(d) {
    return idays[d.day].num * (dim_dispo.width + dim_dispo.mh) ;
}
function dispo_h(d){
    return d.duration * scale ;
}
function gsckd_x(datum,i) {
    return  i*(dim_dispo.width + dim_dispo.mh)
	+ dim_dispo.width * .5;
}
function gsckd_y(datum) {
    return  - .25 * dim_dispo.height ;
}
function gsckh_x(datum) {
    return - dim_dispo.width ;
}
function gsclb_y()  {
    //return dim_dispo.height * .5 * nbSl;
    return dispo_y({start_time:
		    time_settings.time.lunch_break_start_time});
}
function gsclb_x()  {
    return (dim_dispo.width + dim_dispo.mh) * nbPer - dim_dispo.mh ;
}






d3.select("body")
    .on("click", function(d) {
	cancel_cm_adv_preferences();
	cancel_cm_room_tutor_change();
    })


function apply_stype_from_button(save) {
    console.log("app");
//    console.log(document.forms['app']);
    console.log();
    var changes = [] ;
    compute_pref_changes(changes) ;
    var sent_data = {} ;
    sent_data['changes'] = JSON.stringify(changes) ; 

    var se_deb,an_deb,se_fin,an_fin;
    var an, se;
    var se_abs_max = 53;
    var se_min, se_max;

    if(save){
	se_deb = 0 ;
	console.log(annee_courante);
	an_deb = +annee_courante ;
	se_fin = se_deb ;
	an_fin = an_deb ;
    } else {
	se_deb = +document.forms['app'].elements['se_deb'].value ;
	an_deb = +document.forms['app'].elements['an_deb'].value ;
	se_fin = +document.forms['app'].elements['se_fin'].value ;
	an_fin = +document.forms['app'].elements['an_fin'].value ;
    }


    if (an_deb<an_fin ||
        (an_deb==an_fin && se_deb<=se_fin)){


	if(changes.length==0) {
    	    ack = "RAS";
	} else {

	    for (an=an_deb ; an<=an_fin ; an++){
		if(an==an_deb){
		    se_min = se_deb;
		} else {
		    se_min = 1;
		}
		if(an==an_fin){
		    se_max = se_fin;
		} else {
		    se_max = se_abs_max;
		}
		
		for (se=se_min ; se<=se_max ; se++) {

		    //console.log(se,an);
    		    $.ajax({
    			url: url_dispos_changes
			    + "?s=" + se
			    + "&a=" + an
			    + "&u=" + user.nom,
			type: 'POST',
//			contentType: 'application/json; charset=utf-8',
			data: sent_data, //JSON.stringify(changes),
			dataType: 'json',
    			success: function(msg) {

    			},
    			error: function(msg){

    			}
    		    });
		}
	    }
	    ack = "Ok ";
	    if(save){
		ack += "semaine type";
	    } else {
		ack += "semaine "+se_deb+" année "+an_deb
		    +" à semaine "+se_fin+" année "+an_fin;
	    }
	}

    } else {
	ack = "Problème : seconde semaine avant la première";
    }

    document.getElementById("ack").textContent = ack ;
     
}
