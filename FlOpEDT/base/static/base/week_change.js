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



           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
------  ON WEEK CHANGE  ------ 
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */


/*---------------------
  ------- DISPOS ------
  ---------------------*/
function fetch_dispos() {

    fetch.ongoing_dispos = true;

    var exp_week = wdw_weeks.get_selected() ;
    
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_dispos + exp_week.url() ,
        async: true,
        contentType: "text/csv",
        success: function(msg) {
            console.log("in");

            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {
                dispos = {};
                //user.dispos = [];
                d3.csvParse(msg, translate_dispos_from_csv);
		sort_preferences(dispos);
                fetch.ongoing_dispos = false;
                if (ckbox["dis-mod"].cked) {
                    create_dispos_user_data();
                }

                fetch_ended(false);
            }
            show_loader(false);


        },
        error: function(xhr, error) {
            console.log("error");
            console.log(xhr);
            console.log(error);
            console.log(xhr.responseText);
            show_loader(false);
            // window.location.href = url_login;
            window.location.replace(url_login + "?next=" + url_edt + exp_week.year + "/" + exp_week.week);
        }
    });

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_fetch_extra_sched + exp_week.url(),
        async: true,
        contentType: "text/csv",
        success: function(msg) {
            //console.log(msg);
            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {
                extra_pref.tutors = {};
                d3.csvParse(msg, translate_extra_pref_tut_from_csv);
		sort_preferences(extra_pref.tutors);
                var tutors = Object.keys(extra_pref.tutors) ;
                for(i = 0 ; i < tutors.length ; i++) {
                    var busy_days = Object.keys(extra_pref.tutors[tutors[i]]) ;
	            for(d = 0 ; d < busy_days.length ; d++) {
                        fill_holes(extra_pref.tutors[tutors[i]][busy_days[d]], 1);
                    }
                }
            }
            show_loader(false);

        },
        error: function(xhr, error) {
            console.log("error");
            console.log(xhr);
            console.log(error);
            console.log(xhr.responseText);
            show_loader(false);
            // window.location.href = url_login;
            window.location.replace(url_login + "?next=" + url_edt + year_att + "/" + week_att);
        }
    });

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_fetch_shared_rooms + exp_week.url(),
        async: true,
        contentType: "text/csv",
        success: function(msg) {
            console.log("in");
            console.log(msg);
            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {
                extra_pref.rooms = {};
                d3.csvParse(msg, translate_extra_pref_room_from_csv);
	        sort_preferences(extra_pref.rooms);
                console.log(extra_pref.rooms);
                var shared_rooms = Object.keys(extra_pref.rooms) ;
                for(i = 0 ; i < shared_rooms.length ; i++) {
                    var busy_days = Object.keys(extra_pref.rooms[shared_rooms[i]]) ;
	            for(d = 0 ; d < busy_days.length ; d++) {
                        fill_holes(extra_pref.rooms[shared_rooms[i]][busy_days[d]], 1);
                    }
                }
            }
            show_loader(false);

        },
        error: function(xhr, error) {
            console.log("error");
            console.log(xhr);
            console.log(error);
            console.log(xhr.responseText);
            show_loader(false);
            // window.location.href = url_login;
            window.location.replace(url_login + "?next=" + url_edt + year_att + "/" + week_att);
        }
    });


    
}


function translate_dispos_from_csv(d) {
    if(Object.keys(dispos).indexOf(d.prof)==-1){
	dispos[d.prof] = {} ;
        week_days.forEach(function(day) {
	    dispos[d.prof][day.ref] = [] ;
	});	
    }
    dispos[d.prof][d.day].push({start_time:+d.start_time,
			       duration: +d.duration,
			       value: +d.value});
}


function translate_extra_pref_tut_from_csv(d) {
    if(Object.keys(extra_pref.tutors).indexOf(d.tutor)==-1){
	extra_pref.tutors[d.tutor] = {} ;
        for (var i = 0; i < days.length; i++) {
	    extra_pref.tutors[d.tutor][days[i].ref] = [] ;
	}	
    }
    extra_pref.tutors[d.tutor][d.day].push({start_time:+d.start_time,
			             duration: +d.duration,
			             value: 0});
}

function translate_extra_pref_room_from_csv(d) {
    if(Object.keys(extra_pref.rooms).indexOf(d.room)==-1){
	extra_pref.rooms[d.room] = {} ;
        for (var i = 0; i < days.length; i++) {
	    extra_pref.rooms[d.room][days[i].ref] = [] ;
	}	
    }
    extra_pref.rooms[d.room][d.day].push({start_time:+d.start_time,
			                  duration: +d.duration,
			                  value: 0});
}

function sort_preferences(pref) {
    var i, d ;
    var tutors_or_rooms = Object.keys(pref) ;
    for(i = 0 ; i < tutors_or_rooms.length ; i++) {
        week_days.forEach(function(day){
	    pref[tutors_or_rooms[i]][day.ref].sort(
		function (a,b) {
		    return a.start_time - b.start_time ;
		}
	    );
	});
    }
}

// insert a valued interval into a list of valued interval
// (splices it and divides it if needed)
// pref: {start_time, duration, value}
// list: list of pref
function insert_interval(pref, list) {
    var ts = time_settings.time ;

    // starts too early or finishes too late
    if (pref.start_time < ts.day_start_time) {
	pref.duration -= ts.day_start_time - pref.start_time ;
	pref.start_time = ts.day_start_time ;
    }
    if (pref.start_time + pref.duration > ts.day_finish_time) {
	pref.duration -= pref.start_time + pref.duration - ts.day_finish_time ;
    }

    // lunch break
    if (pref.start_time < ts.lunch_break_start_time) {
        // starts in the morning
	if(pref.start_time + pref.duration > ts.lunch_break_start_time) {
	    if(pref.start_time + pref.duration < ts.lunch_break_finish_time) {
                // finishes during lunch break
		pref.duration -= pref.start_time + pref.duration - ts.lunch_break_start_time ;
	    } else {
                // cut by lunch break
		insert_normalized_interval(
		    {start_time: ts.lunch_break_finish_time,
		     duration: pref.start_time + pref.duration - ts.lunch_break_finish_time,
		     value: pref.value},
		    list) ;
		pref.duration = ts.lunch_break_start_time - pref.start_time ;
	    }
	}
    } else if (pref.start_time + pref.duration < ts.lunch_break_finish_time) {
        // fully within lunch break
	return ;
    } else if (pref.start_time < ts.lunch_break_finish_time){
        // starts during lunch break
	pref.duration -= ts.lunch_break_finish_time - pref.start_time ;
	pref.start_time = ts.lunch_break_finish_time ;
    }
    insert_normalized_interval(pref,list);
}

// PRECOND: interval fully within the working hours
// pref: {start_time, duration, value}
// list: list of pref
function insert_normalized_interval(pref, list) {
    //    list.splice(index, nbElements, item)
    list.push(pref);
}


function allocate_dispos(tutor) {
    dispos[tutor] = {} ;
    week_days.forEach(function(day) {
	dispos[tutor][day.ref] = [] ;
    });
}

// -- no slot --
// --  begin  --
// to change, maybe, if splitting intervals is not allowed
// in the interface
function fill_missing_preferences(tutor, ts) {
    week_days.forEach(function(day) {
	insert_interval({start_time: ts.day_start_time,
			 duration: ts.day_finish_time-ts.day_start_time,
			 value: -1},
			dispos[tutor][day.ref]);
    });

}
// --   end   --
// -- no slot --


// -- no slot --
// --  begin  --
// to be cleaned: user.dispos should be avoidable
// off: offset useful for the view. Quite unclean.
function create_dispos_user_data() {

    var d, j, k, d2p, pref_list;
    var ts = time_settings.time ;

    user.dispos = [];
    user.dispos_bu = [];

    var current;

    if (dispos[user.name] === undefined) {
	allocate_dispos(user.name);
	fill_missing_preferences(user.name, ts);
        sort_preferences(dispos);
    }

    week_days.forEach(function(day) {
	pref_list = dispos[user.name][day.ref] ;
	for (var k = 0 ; k<pref_list.length ; k++) {
            d2p = {
		day: day.ref,
		start_time: pref_list[k].start_time,
		duration: pref_list[k].duration,
		val: pref_list[k].value,
		off: -1
            };
            user.dispos_bu.push(d2p);
            if (pref_list[k].value < 0) {
		if (!pref_only) {
                    pref_list[k].val = get_dispos_type(d2p).val;
		} else {
		    pref_list[k].val = par_dispos.nmax;
		}
            }
	    
	    // different object
            user.dispos.push({
		day: day.ref,
		start_time: pref_list[k].start_time,
		duration: pref_list[k].duration,
		val: pref_list[k].value,
		off: -1
            });
	}

    });

    

}
// --   end   --
// -- no slot --



/*---------------------
  ------- WEEKS -------
  ---------------------*/
/*----------------------
  -------- GRID --------
  ----------------------*/
/*----------------------
  ------- GROUPS -------
  ----------------------*/
/*--------------------
  ------ MENUS -------
  --------------------*/
/*----------------------
  ------ MODULES -------
  ----------------------*/
/*--------------------
  ------ PROFS -------
  --------------------*/



/*--------------------
  ------ BKNEWS -------
  --------------------*/
function fetch_bknews(first) {
    fetch.ongoing_bknews = true;

    var exp_week = wdw_weeks.get_selected() ;

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_bknews  + exp_week.url(),
        async: true,
        contentType: "text/csv",
        success: function(msg) {
	    bknews.cont = d3.csvParse(msg,
				      translate_bknews_from_csv);

            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {
		var max_y = -1 ;
		for (var i = 0 ; i < bknews.cont.length ; i++) {
		    if (bknews.cont[i].y > max_y) {
			max_y = bknews.cont[i].y ;
		    }
		}
		bknews.nb_rows = max_y + 1 ;

		adapt_labgp(first);
		if (first) {
		    create_but_scale();
                    if (splash_id == 1) {
                        
	                var splash_mail = {
	                    id: "mail-sent",
	                    but: {list: [{txt: "Ok", click: function(d){ splash_id = 0 ;} }]},
	                    com: {list: [{txt: "E-mail envoyé !", ftsi: 23}]}
	                }
	                splash(splash_mail);
                        
                    } else if (splash_id == 2) {
                        
	                var splash_quote = {
	                    id: "quote-sent",
	                    but: {list: [{txt: "Ok", click: function(d){ splash_id = 0 ; } }]},
	                    com: {list: [{txt: "Citation envoyée ! (en attente de modération)", ftsi: 23}]}
	                }
	                splash(splash_quote);
                        
                    }

		}

		
		
                fetch.ongoing_bknews = false;
                fetch_ended(false);
            }
            show_loader(false);
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });


}

function translate_bknews_from_csv(d){
    return {
	id: +d.id,
	x_beg: +d.x_beg,
	x_end: +d.x_end,
	y: +d.y,
	is_linked: d.is_linked,
	fill_color: d.fill_color,
	strk_color: d.strk_color,
	txt: d.txt
    }
}



function adapt_labgp(first) {
    var expected_ext_grid_dim = dsp_svg.h - dsp_svg.margin.top - dsp_svg.margin.bot ;
    var new_gp_dim;

    if (nbRows > 0) {
	// including bottom garbage
        scale = expected_ext_grid_dim / (nb_minutes_in_grid() + garbage.duration*nbRows) ;
        // if (new_gp_dim > labgp.hm) {
        //     labgp.height = new_gp_dim;
        // } else {
        //     labgp.height = labgp.hm;
        // }
    } // sinon ?
    dsp_svg.h = svg_height() ;
    console.log(dsp_svg.h);
    d3.select("#edt-main").attr("height", dsp_svg.h);

    if (first) {
        window.scroll(0,$("#menu-edt").height());
	expected_ext_grid_dim = dsp_svg.w - dsp_svg.margin.left - dsp_svg.margin.right;
	new_gp_dim = expected_ext_grid_dim / (rootgp_width * week_days.nb_days());
	if (new_gp_dim > labgp.wm) {
            labgp.width = new_gp_dim;
	} else {
            labgp.width = labgp.wm;
	}
        dsp_svg.w = svg_width();
	d3.select("#edt-main").attr("width", dsp_svg.w);
    }

}


/*--------------------
  ------ COURS -------
  --------------------*/

function fetch_cours() {
    fetch.ongoing_cours_pp = true;
    fetch.ongoing_cours_pl = true;
    
    var garbage_plot ;
    
    ack.more = "";

    var exp_week = wdw_weeks.get_selected() ;

    cours_bouge = {};
    
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_cours_pl + exp_week.url() + "/" + num_copie,
        async: true,
        contentType: "text/csv",
        success: function(msg, ts, req) {

            go_regen(null);
            go_alarm_pref();

            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {

                week_days = new WeekDays(JSON.parse(req.getResponseHeader('days').replace(/\'/g, '"')));
            
                tutors.pl = [];
                modules.pl = [];
                salles.pl = [];

                cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);


                fetch.ongoing_cours_pl = false;
                fetch_ended(false);
            }
            show_loader(false);
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });



    if (cours_pp.length > 0){
	garbage_plot = true ;
    } else {
	garbage_plot = false ;
    }

    
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_cours_pp  + exp_week.url() + "/" + num_copie,
        async: true,
        contentType: "text/csv",
        success: function(msg, ts, req) {
            console.log(msg);

            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {

                tutors.pp = [];
                modules.pp = [];
                salles.pp = [];

    		console.log(exp_week,num_copie);

                cours_pp = d3.csvParse(msg, translate_cours_pp_from_csv);

    		if (cours_pp.length > 0 && !garbage_plot){
    		    garbage_plot = true ;
    		    add_garbage();
    		    go_grid(true);
    		} else if (cours_pp.length == 0 && garbage_plot) {
    		    garbage_plot = false ;
    		    remove_garbage();
    		    go_grid(true);
    		}

                fetch.ongoing_cours_pp = false;
                fetch_ended(false);
                show_loader(false);
            }
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });

}


function translate_cours_pl_from_csv(d) {
    var ind = tutors.pl.indexOf(d.prof_name);
    if (ind == -1) {
        tutors.pl.push(d.prof_name);
    }
    if (modules.pl.indexOf(d.module) == -1) {
        modules.pl.push(d.module);
    }
    if (salles.pl.indexOf(d.room) == -1) {
        salles.pl.push(d.room);
    }
    var co = {
        id_course: +d.id_course,
        no_course: +d.num_course,
        prof: d.prof_name,
//        prof_full_name: d.prof_first_name + " " + d.prof_last_name,
        group: translate_gp_name(d.gpe_name),
        promo: set_promos.indexOf(d.gpe_promo),
        mod: d.module,
	c_type: d.coursetype,
        day: d.day,
        start: +d.start_time,
        duration: constraints[d.coursetype].duration,
        room: d.room,
	room_type: d.room_type,
	color_bg: d.color_bg,
	color_txt: d.color_txt,
        display: true
    };
    return co;
}


function translate_cours_pp_from_csv(d) {
    if (tutors.pp.indexOf(d.prof) == -1) {
        tutors.pp.push(d.prof);
    }
    if (modules.pp.indexOf(d.module) == -1) {
        modules.pp.push(d.module);
    }
    if (salles.pp.indexOf(d.room) == -1) {
        salles.pp.push(d.room);
    }
    var co = {
        id_course: +d.id,
        no_course: +d.no,
        prof: d.prof,
        group: translate_gp_name(d.group),
        promo: set_promos.indexOf(d.promo),
        mod: d.module,
	c_type: d.coursetype,
        day: garbage.day,
        start: garbage.start,
        duration: constraints[d.coursetype].duration,
        room: une_salle,
	room_type: d.room_type,
	color_bg: d.color_bg,
	color_txt: d.color_txt,
        display: true
    };
    console.log(co);
    return co;
}



// insert the given week in the side weeks
function insert_side_week(week, days_, courses_) {
    var found = side_courses.find(function(d){
        return Week.compare(d, week) == 0;
    });
    if (typeof found === 'undefined') {
        side_courses.push({
            week: week,
            days: days_,
            courses: courses_
        });
    }
}

// insert in week_set the week of index iweek in weeks.init_data if possible
// return true if it hase been inserted
function insert_in_week_set(week_set, iweek) {
    if (iweek < 0 || iweek >= weeks.init_data.length)  {
        return false ;
    }
    var week = weeks.init_data[iweek].week ;
    var year = weeks.init_data[iweek].year ;
    var found = week_set.find(function(d){
        return d.year == year && d.week == week;
    });
    if (typeof found === 'undefined') {
        week_set.push({
            year: year,
            week: week,
        });
        return true ;
    }
    return false ;
}


// compute which weeks are needed to check the constraints
function which_side_weeks() {
    var week_set = new Weeks() ;
    var fweeks = wdw_weeks.full_weeks ;

    var cur_week_index = wdw_weeks.get_iselected_pure() ;

    // constraint: 'sleep'
    week_set.add_by_index(fweeks, cur_week_index-1) ;
    week_set.add_by_index(fweeks, cur_week_index+1) ;

    // constraint: 'monthly'
    // note: load too much if empty weeks (not in weak_year_init)
    // until day 1 of the month of the first day of the week
    var first_day = week_days.day_by_num(0) ;
    var cur_extremum = first_day.day - 1 ;
    var iextrem = cur_week_index - 1 ;
    while (cur_extremum >= 1) {
        week_set.add_by_index(fweeks, iextrem) ;
        cur_extremum -= 7 ;
        iextrem -= 1 ;
    }

    // until final day of the month of the last day of the week
    var last_day = week_days.day_by_num(week_days.day_list.length -1) ;
    cur_extremum = last_day.day + week_jump ;
    iextrem = cur_week_index + 1 ;
    while (cur_extremum <= last_day.max_days_in_month()) {
        console.log(iextrem);
        week_set.add_by_index(fweeks, iextrem) ;
        cur_extremum += 7 ;
        iextrem += 1 ;
    }

    return week_set ;
}



function side_week_rcv(side_week) {
    return function(msg, ts, req) {

        
        var side_days = new WeekDays(JSON.parse(req.getResponseHeader('days').replace(/\'/g, '"')));
        var side_cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);

        insert_side_week(side_week, side_days, side_cours_pl);
        
    }
}


// fetches courses of the weeks before and after the current week
function fetch_side_weeks() {

    var needed_weeks = which_side_weeks();

    for (var i = 0 ; i < needed_weeks.data.length ; i++) {
        console.log(url_cours_pl + needed_weeks.data[i].url() + "/" + 0);
        $.ajax({
            type: "GET", //rest Type
            dataType: 'text',
            url: url_cours_pl + needed_weeks.data[i].url() + "/" + 0,
            async: true,
            contentType: "text/csv",
            success: side_week_rcv(needed_weeks.data[i]),
            error: function(msg) {
                console.log("error");
            }
        });
        
    }

    
}





// Add pseudo-courses that do not appear in the database //
function add_exception_course(cur_week, cur_year, targ_week, targ_year,
			      day, slot, group, promo, l1, l2, l3) {
    if (cur_week == targ_week && cur_year == targ_year) {
	cours.push({day: day,
		    slot: slot,
		    group: group,
		    promo: set_promos.indexOf(promo),
		    id_course: -1,
		    no_course: -1,
		    mod: l1,
		    prof: l2,
		    room: l3
		   });
    }
}



// Pseudo fonction pour des possibles exceptions //
//
// "Passeport Avenir (Bénéficiaires d'une bourse)"
// "--- 13h30 ---"
// "Amphi 1"
// "exception"
// function add_exception(sem_att, an_att, sem_voulue, an_voulu, nom, l1, l2, l3){
//     if(sem_att==sem_voulue && an_att==an_voulu){
// 	var gro = svg.get_dom("dg").append("g")
// 	    .attr("class",nom);

// 	var tlx = 3*(rootgp_width*labgp.width
// 		     + dim_dispo.plot*(dim_dispo.width+dim_dispo.right))
// 	    + groups[0]["P"].x*labgp.width ;
// 	var tlx2 = tlx + .5*groups[0]["P"].width*labgp.width;

// 	var tly = (3*nbPromos + row_gp[0].y)*(labgp.height) ;
	
// 	gro
// 	    .append("rect")
// 	    .attr("x", tlx  )
// 	    .attr("y", tly )
// 	    .attr("fill","red")
// 	    .attr("width",groups[0]["P"].width*labgp.width)
// 	    .attr("height",labgp.height);

// 	gro.append("text")
// 	    .text(l1)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + labgp.height/4);
// 	gro.append("text")
// 	    .text(l2)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + 2*labgp.height/4);
// 	gro.append("text")
// 	    .text(l3)
// 	    .attr("font-weight","bold")
// 	    .attr("x",tlx2 )
// 	    .attr("y",tly + 3*labgp.height/4);
	
//     } else {
// 	d3.select("."+nom).remove();
//     }
// }


function clean_prof_displayed(light) {

    var tutor_names = tutors.pl;
    for (var i = 0; i < tutors.pp.length; i++) {
        var ind = tutor_names.indexOf(tutors.pp[i]);
        if (ind == -1) {
            tutor_names.push(tutors.pp[i]);
        }
    }

    tutor_names.sort();

    update_selection();

    swap_data(tutor_names, tutors, "tutor") ;

    // relevant tutors
    tutors.all.forEach(function(t) {
        t.relevant = false ;
        if (t.name == user.name) {
            t.relevant = true ;
        }
    });

    if(!light) {
        go_selection_popup() ;
    }
    
}

function translate_gp_name(gp) {
    /*
    var ret = gp.slice(2);
    if (ret == "") {
        ret = "P";
    }
    return ret;
    */
    return gp ;
}



/*--------------------
   ------ ROOMS ------
  --------------------*/
function fetch_unavailable_rooms() {
    fetch.ongoing_un_rooms = true;
    
    var exp_week = wdw_weeks.get_selected() ;

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_unavailable_rooms + exp_week.url() ,
        async: true,
        contentType: "text/csv",
        success: function(msg, ts, req) {
            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {

		console.log(msg);

		clean_unavailable_rooms();
                d3.csvParse(msg, translate_unavailable_rooms);

            }
            show_loader(false);
	    fetch.ongoing_un_rooms = false;
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });
}

function translate_unavailable_rooms(d) {
    var i ;
    console.log(d);
    if (Object.keys(unavailable_rooms).indexOf(d.room)==-1){
	unavailable_rooms[d.room] = {} ; 
	week_days.forEach(function(day){
	    unavailable_rooms[d.room][day.ref] = [] ;
	});
    }
    unavailable_rooms[d.room][d.day].push({start_time: +d.start_time,
					   duration: +d.duration});
}

/*--------------------
   ------ ALL -------
   --------------------*/

function fetch_all(first, fetch_work_copies){
    fetch.done = false;

    fetch.ongoing_cours_pp = true;
    fetch.ongoing_cours_pl = true;
    if (ckbox["dis-mod"].cked || ckbox["edt-mod"].cked) {
	fetch.ongoing_dispos = true;
    }
    if (ckbox["edt-mod"].cked) {
	fetch.ongoing_un_rooms = true;
    }
    fetch.ongoing_bknews = true;

    fetch_version();
    fetch_cours();
    if (ckbox["dis-mod"].cked || ckbox["edt-mod"].cked) {
        fetch_dispos();
    }
    if (ckbox["edt-mod"].cked) {
	fetch_unavailable_rooms() ;
    }
    fetch_bknews(first);

    if(is_side_panel_open && fetch_work_copies) {
        fetch_work_copy_numbers();
    }
}


function fetch_version() {
    var exp_week = wdw_weeks.get_selected() ;

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_week_infos + exp_week.url(),
        async: true,
        contentType: "text/json",
        success: function(msg) {
	    var parsed = JSON.parse(msg);

            var sel_week = wdw_weeks.get_selected() ;
            if (Week.compare(exp_week, sel_week)==0) {
		version = parsed.version ;
		filled_dispos = parsed.proposed_pref ;
		required_dispos = parsed.required_pref ;
		go_regen(parsed.regen);
            }
	    
            show_loader(false);
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });

}

function translate_version_from_csv(d){
    return +d.version ;
}


function fetch_ended(light) {
    if (!fetch.ongoing_cours_pl &&
        !fetch.ongoing_cours_pp) {
        cours = cours_pl.concat(cours_pp);

        var module_names = modules.pl;
        for (var i = 0; i < modules.pp.length; i++) {
            if (module_names.indexOf(modules.pp[i]) == -1) {
                module_names.push(modules.pp[i]);
            }
        }

        module_names.sort();

        update_selection();

        swap_data(module_names, modules, "module");

        update_active();
        update_relevant();

        salles.all = [""].concat(salles.pl);
        for (var i = 0; i < salles.pp.length; i++) {
            if (salles.all.indexOf(salles.pp[i]) == -1) {
                salles.all.push(salles.pp[i]);
            }
        }

        salles.all.sort();

        if (salles.all.indexOf(salles.sel) == -1) {
            salles.sel = "";
        }

        clean_prof_displayed(light);
    }

    if (!fetch.ongoing_cours_pp &&
        !fetch.ongoing_cours_pl &&
        !fetch.ongoing_dispos   &&
        !fetch.ongoing_un_rooms &&
        !fetch.ongoing_bknews) {

        fetch.done = true;
        go_edt(false);

    }
}

// - store old data in old
// - translate fetched into current (keeping display values)
function swap_data(fetched, current, type) {
    current.old = current.all ;
    current.all = fetched.map(
        function(m) {
            var em = {} ;
            em.name = m ;
            var oldf = current.old.find(function(mo) {
                return mo.name == m ;
            });
            var avail = sel_popup.get_available(type);
            if (typeof avail === 'undefined') {
                em.display = true ;
            } else {
                em.display = !(avail.active) ;
            }
            if (typeof oldf !== 'undefined') {
                em.display = oldf.display ;
            }
            return em ;
        }
    )
    var panel = sel_popup.panels.find(function(p) {
        return p.type == type ;
    })
    if (typeof panel !== 'undefined') {
        panel.list = current.all ;
    }

}







/* 
Reste :
  x couleur modules
  x display filtre prof
  x weeks (fetch, go_course, go_dispo)
  x base edt (d&d, struct edt, check, display conflits, week pro)
  o base dispos (simple, 0-9, week type)
  o plot par défaut
  x move next week
*/

/*
Fichiers :
-> better.js           -- static
-> better-groupes.json -- static
-> better-cours.csv    -- dynamic
-> better-dispos.json  -- dynamic
-> better-salles.json  -- 
<-  
*/

/*
Checks :
o on a la dispo de tous les profs

*/

/*
https://www.youtube.com/watch?v=XNzKZ7lJRUc

*/





/*

function fetchjson() {
    console.log("in");
    $.ajax({
        type: "GET", //rest Type
        dataType: 'json', //mispelled
        url: url_json,
        async: false,
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            console.log(msg);
	    var data = JSON.parse(msg);
            console.log(data);
            console.log("success");
        },
	error: function(msg) {
	    console.log("error");
	},
	complete: function(msg) {
	    console.log("complete");
	}
    });
    console.log("out");
}

*/


/*
Harmonisations :
- noms groupes
- promo 0-1 ou 1-2
*/
