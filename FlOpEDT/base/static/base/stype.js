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

dsp_svg.margin = {top: 50,  left: 100, right: 10, bot:10};

dsp_svg.h = 625 - dsp_svg.margin.top - dsp_svg.margin.bot ;
dsp_svg.w = 680 - dsp_svg.margin.left - dsp_svg.margin.right ;

dsp_svg.cadastre = [
    // valider
    ["svg","vg"],
    // background, middleground, foreground, dragground
    ["svg","edtg"],
    ["edtg","edt-bg"],
    ["edtg","edt-mg"],
    ["edtg","edt-fg"],
    // context menus ground
    ["svg","cmg"],
    ["cmg","cmpg"],
    ["cmg","cmtg"],
    // drag ground
    ["svg","dg"]
];



var mode = "tutor" ;

var dd_selections = {
    'tutor': {value:logged_usr.nom},
    'prog': {value:''},
    'type': {value:''}};



smiley.tete = 13 ;

dim_dispo.width  = 80 ;
dim_dispo.height = 500 ;
dim_dispo.mh = 10 ;
dim_dispo.plot = 1 ;
nbRows=1;
scale = dim_dispo.height / nb_minutes_in_grid()  ;


ckbox["dis-mod"].cked = true ;

pref_only = true ;




svg = new Svg(dsp_svg.layout_tree, false);
svg.create_container(true);
svg.create_layouts(dsp_svg.cadastre) ;

var days_header = new WeekDayHeader(svg, "edt-fg", week_days, false, null) ;

// overwrite functions for headers
function WeekDayMixStype() {
    this.gsckd_x = function(datum,i) {
        return  i*(dim_dispo.width + dim_dispo.mh)
	    + dim_dispo.width * .5;
    }
    this.gsckd_y = function(datum) {
        return  - 20 ;
    }
    this.gsckd_txt = function(d) {
        return  d.name ;
    }
    this.gsckh_x = function(datum) {
        return - dim_dispo.width ;
    }
}
Object.assign(days_header.mix, new WeekDayMixStype()) ;
hard_bind(days_header.mix);

var hours_header = new HourHeader(svg, "edt-fg", hours) ;



go_days(true, false);
create_lunchbar();
fetch_pref_only();





function create_lunchbar() {
    svg.get_dom("edt-fg")
	.append("line")
	.attr("class","lunchbar")
	.attr("stroke","black")
	.attr("stroke-width",6)
	.attr("x1",0)
	.attr("y1",gsclb_y)
	.attr("x2",gsclb_x)
	.attr("y2",gsclb_y);

}



/*---------------------
  ------- DISPOS ------
  ---------------------*/
function fetch_url() {
    if (mode == 'tutor') {
        return url_fetch_user_dweek + user.nom ;
    } else if (mode == 'course') {
        return url_fetch_course_dweek 
            + dd_selections['prog'].value
            + '/' + dd_selections['type'].value ;
    }
}


function course_type_prog_name(prog, ctype){
    return prog + '--' + ctype ;
}


function translate_course_preferences_from_csv(d) {
    var pseudo_tutor = course_type_prog_name(d.train_prog, d.type_name) ;
    if(Object.keys(dispos).indexOf(pseudo_tutor)==-1){
	dispos[pseudo_tutor] = {} ;
        week_days.forEach(function(day) {
	    dispos[pseudo_tutor][day.ref] = [] ;
	});
    }
    dispos[pseudo_tutor][d.day].push({start_time:+d.start_time,
			       duration: +d.duration,
			       value: +d.valeur});
}


function translate_pref_from_csv(d) {
    if (mode == 'tutor') {
        return translate_dispos_from_csv(d);
    } else if (mode == 'course') {
        return translate_course_preferences_from_csv(d);
    }
}



function fetch_pref_only() {
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: fetch_url() ,
        async: false,
        contentType: "text/csv",
        success: function (msg) {
	    console.log(msg);
	    
	    console.log("in");
            dispos = {} ;
	    user.dispos_type = [] ;
	    user.dispos_type = d3.csvParse(msg, translate_pref_from_csv);
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
    return week_days.day_by_ref(d.day).num * (dim_dispo.width + dim_dispo.mh) ;
}
function dispo_h(d){
    return d.duration * scale ;
}



function gsclb_y()  {
    return dispo_y({start_time:
		    time_settings.time.lunch_break_start_time});
}
function gsclb_x()  {
    return (dim_dispo.width + dim_dispo.mh) * week_days.nb_days() - dim_dispo.mh ;
}






d3.select("body")
    .on("click", function(d) {
	cancel_cm_adv_preferences();
	cancel_cm_room_tutor_change();
    })



// compute url to send preference changes to
// according to mode
function send_url(year, week) {
    if (mode == 'tutor') {
        return url_user_pref_changes + year + "/" + week
	    + "/" + user.nom ;
    } else if (mode == 'course') {
        return url_course_pref_changes + year + "/" + week
	    + "/" + dd_selections['prog'].value
            + "/" + dd_selections['type'].value ;
    }
}


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
    	    ack.pref = "RAS";
            document.getElementById("ack").textContent = ack.pref ;
	} else {

            ack.pref = "Ok ";
	    if(save){
		ack.pref += "semaine type";
	    } else {
		ack.pref += "semaine "+se_deb+" année "+an_deb
		    +" à semaine "+se_fin+" année "+an_fin;
	    }


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
                    show_loader(true);
    		    $.ajax({
    			url: send_url(an, se),
			type: 'POST',
//			contentType: 'application/json; charset=utf-8',
			data: sent_data, //JSON.stringify(changes),
			dataType: 'json',
    			success: function(msg) {
                            if(msg.status != 'OK') {
                                ack.pref = msg.more ;
                            }
                            document.getElementById("ack").textContent = ack.pref ;
                            show_loader(false);
    			},
    			error: function(msg){
                            ack.pref = 'Pb communication serveur';
                            document.getElementById("ack").textContent = ack.pref ;
                            show_loader(false);
    			}
    		    });
		}
	    }
	}

    } else {
	ack.pref = "Problème : seconde semaine avant la première";
        document.getElementById("ack").textContent = ack.pref ;
    }

     
}
