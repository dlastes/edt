           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------     ACTIONS    -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */



/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// apply pref change when simple mode
function apply_change_simple_pref(d) {
    if (ckbox["dis-mod"].cked) {
        if (Math.floor(d.val % (par_dispos.nmax / 2)) != 0) {
            d.val = Math.floor(d.val / (par_dispos.nmax / 2)) * par_dispos.nmax / 2;
        }
        d.val = (d.val + par_dispos.nmax / 2) % (3 * par_dispos.nmax / 2);
        dispos[user.nom][d.day][d.hour] = d.val;
        user.dispos[day_hour_2_1D(d)].val = d.val;
        go_pref(true);
    }
}

/*---------------------
  ------- WEEKS -------
  ---------------------*/

// move timeline to the left
function week_left() {
    if (weeks.fdisp > 0) {
        weeks.fdisp -= 1;
        weeks.cur_data.pop();
        weeks.cur_data.unshift(weeks.init_data[weeks.fdisp]);
    }
    go_week_menu(false);
}

// move timeline to the right
function week_right() {
    if (weeks.fdisp + weeks.ndisp + 2 < weeks.init_data.length) {
        weeks.fdisp += 1;
        weeks.cur_data.splice(0, 1);
        weeks.cur_data.push(weeks.init_data[weeks.fdisp + weeks.ndisp + 1]);
    }
    go_week_menu(false);
}


// change week
// Not sure ok even if user is quick (cf fetch_cours)
function apply_wk_change(d, i) { //if(fetch.done) {
    if (i > 0 && i <= weeks.ndisp) {
        weeks.sel[0] = i + weeks.fdisp;
    }
    dispos = [];
    user.dispos = [];
    fetch.cours_ok = false;
    fetch.dispos_ok = false;


    fetch_cours();

    fetch_bknews(false);

    
    if (ckbox["dis-mod"].cked) {
        fetch_dispos();
    };

    go_week_menu(false);
} //}


/*----------------------
  -------- GRID --------
  ----------------------*/

// clear pop message when unauthorized course modification
function clear_pop(gs) {
    if (gs.pop) {
        gs.pop = false;
        gs.display = false;
        gs.reason = "";
        go_grid(false);
    }
}


/*---------------------
  ------- TUTORS ------
  ---------------------*/

// apply changes in the display of tutor pr
function apply_tutor_display(pr) {
    if (fetch.done) {
	if(logged_usr.dispo_all_change && ckbox["dis-mod"].cked){
	    prof_displayed = [pr] ;
	    user.nom = pr ;
	    create_dispos_user_data() ;
	    go_pref(true) ;
	} else {
            if (prof_displayed.indexOf(pr) > -1) {
		if (prof_displayed.length == profs.length) {
                    prof_displayed = [pr];
		} else {
                    var ind = prof_displayed.indexOf(pr);
                    prof_displayed.splice(ind, 1);
                    if (prof_displayed.length == 0) {
			prof_displayed = profs.slice(0);
                    }
		}
            } else {
		prof_displayed.push(pr);
            }
	}

            go_tutors();
    }
}


// display all tutors
function apply_tutor_display_all() {
    if (fetch.done
	&& (!logged_usr.dispo_all_change || !ckbox["dis-mod"].cked)) {
        prof_displayed = profs.slice(0);
        go_tutors();
    }
}

/*----------------------
  ------- GROUPS -------
  ----------------------*/


var is_no_hidden_grp = true;

function check_hidden_groups() {
    is_no_hidden_grp = true;
    for (var a in groups) {
        for (var g in groups[a]) {
            if (groups[a][g].display == false) {
                is_no_hidden_grp = false;
                return;
            }
        }
    }
}

function are_all_groups_hidden() {
    // if all groups are hidden
    // all groups are automatically displayed
    for (var a in groups) {
        for (var g in groups[a]) {
            if (groups[a][g].display == true) {
                return;
            }
        }
    }
    set_all_groups_display(true);
}

function set_all_groups_display(isDisplayed) {
    for (var a in groups) {
        for (var g in groups[a]) {
            groups[a][g].display = isDisplayed;
        }
    }
}


// apply changes in the display of group gp
// start == true iff a particular group is chosen by a GET request
// go_button == true iff the group buttons are to be updated
function apply_gp_display(gp, start, go_button) {
    if (fetch.done || start) {
        if (is_no_hidden_grp) {
            set_all_groups_display(false);
            gp.display = true;
        } else {
            gp.display = !gp.display;
        }

        propagate_display_up(gp, gp.display);
        propagate_display_down(gp, gp.display);

        are_all_groups_hidden(); // all hidden => all displayed
        check_hidden_groups();

        update_all_groups();
	if (go_button) {
            go_gp_buttons();
	}
    }
    if (fetch.done) {
        go_edt();
    }
}


// set to boolean b the attribute display of every group
// that is a descendant of gp, gp included
function propagate_display_down(gp, b) {
    gp.display = b;
    for (var i = 0; i < gp.children.length; i++) {
        propagate_display_down(groups[gp.promo][gp.children[i]], b);
    }
}

// set to boolean b the attribute display of every group
// that is an ancestor of gp, gp included
function propagate_display_up(gp, b) {
    gp.display = b;
    if (gp.parent != null) {
        if (b) { // ancestors should be displayed too 
            propagate_display_up(groups[gp.promo][gp.parent], true);
        } else { // is there any sibling still displayed?
            var i = 0;
            var hidden_child = true;
            while (hidden_child && i < groups[gp.promo][gp.parent].children.length) {
                if (groups[gp.promo][groups[gp.promo][gp.parent].children[i]].display) {
                    hidden_child = false;
                } else {
                    i += 1;
                }
            }
            if (hidden_child) {
                propagate_display_up(groups[gp.promo][gp.parent], false);
            }
        }
    }
}


/*--------------------
  ------ MENUS -------
  --------------------*/

// apply the updates resulting from a change in a checkbox
function apply_ckbox(dk) {
    if (ckbox[dk].en && fetch.done) {

        if (ckbox[dk].cked) {
            ckbox[dk].cked = false;
        } else {
            ckbox[dk].cked = true;
        }

        if (dk == "dis-mod") {
            if (ckbox[dk].cked) {
                //create_dispos_user_data();
                //ckbox["dis-mod"].disp = true;
                stg.attr("visibility", "visible");

                dim_dispo.plot = 1;
                if (rootgp_width != 0) {
                    labgp.width *= 1 - (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
                }
                if (!fetch.dispos_ok) {
                    fetch_dispos();
                } else {
                    if (user.dispos.length == 0) {
                        create_dispos_user_data();
                    }
                    go_edt(false);
                }
            } else {
                user.dispos = [];
                //ckbox["dis-mod"].disp = false;
                stg.attr("visibility", "hidden");
                dim_dispo.plot = 0;
                if (rootgp_width != 0) {
                    labgp.width *= 1 + (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
                }
                go_edt(false);
            }
        } else if (dk == "edt-mod") {
            if (ckbox[dk].cked) {
		if (total_regen) {

		    ckbox[dk].cked = false ;
		
		    var splash_disclaimer = {
			id: "disc-edt-mod",
			but: {list: [{txt: "Ok", click: function(d){} }]},
			com: {list: [{txt: "Avis", ftsi: 23}, {txt: ""},
				     {txt: "L'emploi du temps va être regénéré totalement (cf. en bas à droite)."},
				     {txt: "Contentez-vous de mettre à jour vos disponibilités : elles seront prises en compte lors de la regénération."}]}
		    }
		    splash(splash_disclaimer);
		    
		    return ;
		}
		
                edt_but.attr("visibility", "visible");
                if (!fetch.dispos_ok) {
                    fetch_dispos();
                } else {
                    go_edt(true);
                }
            } else {
                edt_but.attr("visibility", "hidden");
                go_edt(true);
            }
        } else {
            go_edt(true);
        }
        // Fetch data, ask for login, etc.
        // ...

        stg
            .select("[but=st-ap]")
            .attr("cursor", st_but_ptr());



        go_menus();
    }
}



/*-----------------------
   ------ VALIDATE ------
   ----------------------*/

function compute_changes(changes, profs, gps) {
    var i, id, change, prof_changed, gp_changed, gp_named;

    var cur_course, cb ;

    
    for (i = 0; i < Object.keys(cours_bouge).length ; i++) {
	id = Object.keys(cours_bouge)[i] ;
	cur_course = get_course(id) ;
	cb = cours_bouge[id] ;

	if (had_moved(cb , cur_course)) {

	    // add instructor if never seen
            if (profs.indexOf(cur_course.prof) == -1
		&& cur_course.prof != logged_usr.nom) {
                profs.push(cur_course.prof);
            }

	    // add group if never seen
	    gp_changed = groups[cur_course.promo][cur_course.group] ;
	    if (set_promos[gp_changed.promo] == 3) {
		gp_named = "LP" ;
	    } else {
		gp_named = set_promos[gp_changed.promo] + "A";
		if(gp_changed.nom != "P") {
		    gp_named += gp_changed.nom ;
		}
	    }
            if (gps.indexOf(gp_named) == -1) {
                gps.push(gp_named);
            }
	    

	    // build the communication with django
	    
            change = {id: id,
		      day: {o: cb.day,
			    n: null },
		      slot: {o: cb.slot,
			     n: null },
		      room: {o: cb.room,
			     n: null },
		      week: {o: weeks.init_data[weeks.sel[0]].semaine,
			     n: null },
		      year: {o: weeks.init_data[weeks.sel[0]].an,
			     n: null}
		     };
	    
	    
            console.log("change", change);
            if (is_garbage(cur_course.day, cur_course.slot)) {
		alert("Il y a des cours non placés.");
            } else if (is_free(cur_course.day,
			       cur_course.slot,
			       cur_course.promo)) {
		alert("Pas de cours pour les " +
                      set_promos[cur_course.promo] + "A"
		      + " le " + data_grid_scale_day[cur_course.day]
		      + " sur le créneau "
		      + data_grid_scale_hour[cur_course.slot]
		      + ".");
            } else {
		
		if (cb.day != cur_course.day ||
                    cb.slot != cur_course.slot) {
                    change.day.n = cur_course.day;
                    change.slot.n = cur_course.slot;
		}
		if (cb.room != cur_course.room) {
                    change.room.n = cur_course.room;
		}

		changes.push(change);
		
            }
	    
	}


    }
    
    console.log(JSON.stringify({
        v: version,
        tab: changes
    }));

}


function confirm_change() {
    var changes, profs_conc, gps, i, prof_txt, gp_txt;
    changes = [];
    profs_conc = [];
    gps = [];
    compute_changes(changes, profs_conc, gps);

    if (changes.length == 0) {
        ack.edt = "modif EdT : RAS";
        go_ack_msg(true);
    } else {

        if (profs_conc.length > 0) {
            prof_txt = "Avez-vous contacté " ;
	    prof_txt += array_to_msg(profs_conc) ;
	    prof_txt += " ?" ;
	} else {
            prof_txt = "Tudo bem ?" ;
	}

        gp_txt = "(Par ailleurs, ce serait bien de prévenir ";
	if (gps.length == 1) {
	    gp_txt += "le groupe ";
	} else {
	    gp_txt += "les groupes ";
	}
	gp_txt += array_to_msg(gps) ;
        gp_txt += ").";


	var splash_confirm = {
	    id: "conf-chg",
	    but: {list: [{txt: "Oui", click: function(d){send_edt_change(changes);}},
			 {txt: "Non", click: function(d){} }]},
	    com: {list: [{txt: prof_txt},
			 {txt:gp_txt}]}
	}

	splash(splash_confirm);

    }
}


function array_to_msg(a) {
    console.log(a);
    var i ;
    var ret = "" ;
    for (i = 0; i < a.length - 2 ; i++) {
	ret += a[i] + ", " ;
    }
    if (a.length > 1) {
	ret += a[a.length - 2] + " et "
	    + a[a.length - 1] ;
    } else {
	ret += a[0] ;
    }
    return ret ;
}



function send_edt_change(changes) {
    show_loader(true);
    $.ajax({
        url: url_edt_changes
	    + "?s=" + weeks.init_data[weeks.sel[0]].semaine
	    + "&a=" + weeks.init_data[weeks.sel[0]].an
	    + "&c=" + num_copie,
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({
            v: version,
            tab: changes
        }),
        dataType: 'json',
        success: function(msg) {
            edt_change_ack(msg);
            show_loader(false);
        },
        error: function(msg) {
            edt_change_ack(msg);
            show_loader(false);
        }
    });
}




function send_dis_change() {
    var changes = [];
    var nbDispos = 0;

    if (user.dispos_bu.length == 0) {
        ack.edt = "modif dispo : RAS";
        go_ack_msg(true);
        return;
    }

    for (var i = 0; i < Object.keys(user.dispos).length; i++) {
        if (user.dispos[i].val > 0) {
            nbDispos++;
        }
        if (user.dispos[i].val != user.dispos_bu[i].val) {
            changes.push(user.dispos[i]);
        }
        user.dispos_bu[i].day = user.dispos[i].day;
        user.dispos_bu[i].hour = user.dispos[i].hour;
        user.dispos_bu[i].val = user.dispos[i].val;
        user.dispos_bu[i].off = user.dispos[i].off;
    }



    // console.log(nbDispos);
    // console.log(changes);
    // console.log(JSON.stringify({create: create, tab: changes}));
    // console.log(JSON.stringify(changes));


    if (changes.length == 0) {
        ack.edt = "modif dispo : RAS";
        go_ack_msg(true);
    } else {

        show_loader(true);
        $.ajax({
            url: url_dispos_changes
		+ "?s=" + weeks.init_data[weeks.sel[0]].semaine
		+ "&a=" + weeks.init_data[weeks.sel[0]].an
		+ "&u=" + user.nom,
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(changes),
            dataType: 'json',
            success: function(msg) {
                show_loader(false);
                return dis_change_ack(msg, nbDispos);
            },
            error: function(msg) {
                show_loader(false);
                return dis_change_ack(msg, nbDispos);
            }
        });
    }


}




function edt_change_ack(msg) {
    if (msg.responseText == "OK") {
        version += 1;
        ack.edt = "modifications EDT : OK !";
        cours_bouge = [];
    } else {
        ack.edt = msg.getResponseHeader('reason');
        if (ack.edt.startsWith("Version")) {
            ack.edt += "\nQuelqu'un a\nmodifié entre-temps."
        } else {
            ack.edt += "\nCall PSE or PRG"
        }
    }
    console.log(ack.edt);
    go_ack_msg(true);
}


function dis_change_ack(msg, nbDispos) {
    console.log(msg);
    if (msg.responseText == "OK") {
        ack.edt = "modifications dispos : OK !"
    } else {
        ack.edt = msg.getResponseHeader('reason');
        ack.edt += "\nCall PSE or PRG"
    }
    go_ack_msg(true);

    filled_dispos = nbDispos;
    go_alarm_pref();

}



/*--------------------
   ------ SLASH ------
  --------------------*/



function clean_splash(class_id) {
    dg.select("." + class_id).remove() ;
}



function splash(splash_ds){

    if (splash_ds.bg === undefined) {
	splash_ds.bg = {x:0,
			y:0,
			width: grid_width(),
			height: grid_height()};// + valid.margin_edt + 1.1 * valid.h} ;
	
    }

    var wp = splash_ds.bg ;

    var class_id = "spl_" + splash_ds.id ;

    dg
	.select("." + class_id)
	.remove();
    
    dg
        .append("g")
        .attr("class", class_id)
        .append("rect")
        .attr("x", wp.x)
        .attr("y", wp.y)
        .attr("width", wp.width)
        .attr("height", wp.height)
        .attr("fill", "white");

    var spg = dg.select("." + class_id) ;


    
    var  i, f ;

    var but_par = splash_ds.but ;

    if (but_par.slack_y === undefined) {
	but_par.slack_y = valid.h ;
    }
    if (but_par.slack_x === undefined) {
	but_par.slack_x = 90 ;
    }
    if (but_par.width === undefined) {
	but_par.width = valid.w;
    }
    if (but_par.height === undefined) {
	but_par.height = valid.h;
    }

    
    var but_dat = but_par.list ;
    var init_but_x = wp.x + .5*wp.width
	- .5 * (but_dat.length * but_par.width
		+ (but_dat.length - 1) * but_par.slack_x) ;
    var init_but_y = wp.y + wp.height - but_par.height - but_par.slack_y ;
    for (i = 0 ; i < but_dat.length; i++){
	f = but_dat[i].click ;
	but_dat[i].x = init_but_x + i * (but_par.width + but_par.slack_x) ;
	but_dat[i].y = init_but_y ;
	but_dat[i].w = but_par.width ;
	but_dat[i].h = but_par.height ;
    }



    var buts = spg
	.selectAll(".but")
	.data(but_dat)
	.enter()
	.append("g")
        .attr("cursor", "pointer")
        .attr("class", "but")
	.on("click", function(d) { d.click(d); clean_splash(class_id); } );
    

    buts
        .append("rect")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", classic_x)
        .attr("y", classic_y)
        .attr("width", classic_w)
        .attr("height", classic_h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2);

    buts
	.append("text")
	.attr("style", function(d){
	    return "text-anchor: middle; font-size: 18";
	})
        .attr("x", classic_txt_x)
        .attr("y", classic_txt_y)
        .text(classic_txt);



    var com_par = splash_ds.com ;

    if (com_par.x === undefined) {
	com_par.x = .5 * grid_width();
    }
    if (com_par.slack_y === undefined) {
	com_par.slack_y = 50 ;
    }
    if (com_par.anch === undefined) {
	com_par.anch = "middle" ;
    }


    
    var com_dat = com_par.list ;
    var init_com_y = wp.y + .5*(wp.height - but_par.height - 2* but_par.slack_y)
	- .5 * (com_dat.length  * com_par.slack_y) ;
    for (i = 0 ; i < com_dat.length; i++){
	com_dat[i].x = com_par.x ;
	com_dat[i].y = init_com_y + i * com_par.slack_y ;
	if (com_dat[i].ftsi === undefined) {
	    com_dat[i].ftsi = 18 ;
	}
    }

    console.log(com_dat);


    var comms = spg
	.selectAll(".comm")
	.data(com_dat)
	.enter();


    comms
        .append("text")
        .attr("class", "comm")
	.attr("style", function(d){
	    return "text-anchor: "+d.anch
		+"; font-size:" + d.ftsi;
	})
        .attr("x", classic_x)
        .attr("y", classic_y)
        .text(classic_txt);
    
}








/*--------------------
   ------ STYPE ------
  --------------------*/

function apply_stype() {
    if (ckbox["dis-mod"].cked) {
        for (var d = 0; d < user.dispos.length; d++) {
            user.dispos[d].day = user.dispos_type[d].day;
            user.dispos[d].hour = user.dispos_type[d].hour;
            user.dispos[d].val = user.dispos_type[d].val;
            user.dispos[d].off = user.dispos_type[d].off;
            dispos[user.nom][user.dispos[d].day][user.dispos[d].hour] = user.dispos[d].val;
        }
        go_pref(true);
        send_dis_change();
    }
}



/*--------------------
   ------ ALL -------
  --------------------*/
function add_bouge(d) {

    console.log("new");
    if (Object.keys(cours_bouge).indexOf(d.id_cours.toString()) == -1) {
        cours_bouge[d.id_cours] = {
            id: d.id_cours,
            day: d.day,
            slot: d.slot,
            room: d.room
        };
        console.log(cours_bouge[d.id_cours]);
    }
}

function had_moved(cb, c){
    return cb.day != c.day
	|| cb.slot != c.slot
	|| cb.room != c.room ;
}


function get_course(id){
    var found = false ;
    var i = 0 ;
    
    while (i < Object.keys(cours).length && !found) {
	if (cours[i].id_cours == id){
	    found = true ;
	} else {
	    i ++ ;
	}
    }

    if (found) {
	return cours[i] ;
    } else {
	return null ;
    }
    
}
