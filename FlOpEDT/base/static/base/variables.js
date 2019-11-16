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

/* INPUTS

// var user = {nom: string,
// 	    dispos: [],
// 	    dispos_bu: [],
// 	    dispos_type: [],
// 	   };

// var margin = {top: nb, left: nb, right: nb, bot: nb};

// var svg = {height: nb, width: nb};

// var week = nb ;
// var year = nb;

// var labgp = {height: nb, width: nb, tot: nb, height_init: nb, width_init: nb};

// var dim_dispo = {height:2*labgp.height, width: 60, right: 10, plot:0,
// 		 adv_v_margin: 5};

*/
           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------  VAR GLOBALES  -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
           \     */

/*--------------------------
  ------- TIME ------
  --------------------------*/

// day indices
var idays = {} ;
for (var i = 0 ; i<days.length ; i++){
    idays[days[i].ref] = days[i] ;
}

// side time scale: list of {h: int, hd:('am'|'pm')}
var side_time = [] ;
var stime = Math.floor(time_settings.time.day_start_time/60) ;
if (stime*60 < time_settings.time.day_start_time) {
    stime ++ ;
}
while (stime*60 <= time_settings.time.day_finish_time) {
    if(stime*60 <= time_settings.time.lunch_break_start_time) {
        side_time.push({h:stime, hd:'am'});
    }
    if (stime*60 >= time_settings.time.lunch_break_finish_time) {
        side_time.push({h:stime, hd:'pm'});
    }
    stime ++ ;
}


/*-------------------------
  - CONTEXT MENUS HELPERS -
  -------------------------*/

function cancel_cm_adv_preferences(){
    if(ckbox["dis-mod"].cked) {
	if(! context_menu.dispo_hold) {
	    data_dispo_adv_cur = [] ;
	    go_cm_advanced_pref(true);
	}
	context_menu.dispo_hold = false ;
    }
}

function cancel_cm_room_tutor_change(){
    if(ckbox["edt-mod"].cked) {
	if(!context_menu.room_tutor_hold) {
            if(pending.init_course!=null) {
                pending.back_init() ;
		room_tutor_change.proposal = [] ;
		go_cm_room_tutor_change();
                go_courses(false) ;
	    }
	}
	context_menu.room_tutor_hold = false ;
    }
}




/*-----------------------------
   ------ file fetchers -------
  -----------------------------*/

var file_fetch =
    {groups: {done: false, data: null, callback: null},
     constraints: {done: false, data: null, callback: null},
     rooms: {done:false, data: null, callback: null},
     department: {done:false, data: null, callback: null},};

function main(name, data) {
    file_fetch[name].data = data ;
    file_fetch[name].done = true ;
    if(file_fetch.groups.done && file_fetch.constraints.done
       && file_fetch.rooms.done && file_fetch.department.done) {
        file_fetch.constraints.callback();
        file_fetch.rooms.callback();
        file_fetch.department.callback();
        file_fetch.groups.callback();
    }
}

file_fetch.rooms.callback = function () {
    rooms = this.data;
    var room_names ;
    room_names = Object.keys(rooms.roomgroups) ;
    swap_data(room_names, rooms_sel, "room");
} ;

file_fetch.constraints.callback = function () {
    constraints = this.data;

    // rev_constraints only used in slot_case
    var i, j, coursetypes, cur_start_time ;
    coursetypes = Object.keys(constraints) ;
    for(i=0 ; i<coursetypes.length ; i++) {
	for(j=0 ; j<constraints[coursetypes[i]].allowed_st.length ; j++){
            cur_start_time = constraints[coursetypes[i]].allowed_st[j].toString() ;
            if (! Object.keys(rev_constraints).includes(cur_start_time)) {
	        rev_constraints[cur_start_time]
		    = constraints[coursetypes[i]].duration ;
            }
	}
    }
    rev_constraints[garbage.start.toString()] = garbage.duration ;

    
    fetch.constraints_ok = true;
    create_grid_data();
}

file_fetch.department.callback = function () {
    departments.data = this.data ;
    //create_dept_redirection();
} ;



/*--------------------
   ------ ALL -------
  --------------------*/

// number of days in the week
var nbPer = Object.keys(idays).length ;


// -- no slot --
// --  begin  --
// TO BE REMOVED: still appears in stype.js
// number of slots within 1 day
var nbSl = 6;
// --   end   --
// -- no slot --

// initial number of promos
var slot_case = false ; //true ;

// current number of rows
var nbRows;
// last positive number of rows
var pos_nbRows = 0;

// maximum number of lab groups among promos
var rootgp_width = 0;
// last positive number of lab groups
var pos_rootgp_width = 0;

// different grounds where to plot
var fg, mg, bg, dg, meg, vg, gpg, catg, stg, mog, sag, fig, log, cmpg, cmtg, selg, pmg;
var wg = {
    upper: null,
    bg: null,
    fg: null
};

// opacity of disabled stuffs
var opac = .4;


// status of fetching (cours_pl : cours placés, cours_pp : cours pas placés)
var fetch = {
    ongoing_cours_pl: false,
    ongoing_dispos: false,
    ongoing_cours_pp: false,
    ongoing_bknews: false,
    ongoing_un_rooms: false,
    done: false,
    cours_ok: false,
    dispos_ok: false,
    groups_ok: false,
    constraints_ok: false
};
//cours_ok pas très utile


var svg_cont ;




/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// 2D array of list (username,iday,list of intervals)
  // 
var dispos = {};
  // unavailabilities due to other departments
var extra_pref = {tutors:{},
                  rooms:{}};

// parameters for availability
var par_dispos = {
    nmax: 8, // maximum happiness
    adv_red: .7, // width of dd menu
    // compared to dispo cell
    rad_cross: .6, // radius of + circle
    // compared to smiley
    red_cross: .3 // length of + branches
        // compared to smiley
};

// parameters for the smileys
var smiley = {
    tete: 10,
    oeil_x: .35,
    oeil_y: -.35,
    oeil_max: .08,
    oeil_min: .03,
    bouche_x: .5,
    bouche_haut_y: -.1,
    bouche_bas_y: .6,
    sourcil: .4,
    init_x: 0,
    init_y: -180,
    max_r: 1,
    mid_o_v: 0xA5 * 100 / 255,
    mid_y_v: 0xE0 * 100 / 255,
    min_v: 0x90 * 100 / 255,
    rect_w: 1.1,
    rect_h: .3
};

// helper arrays for smileys
var data_dispo_adv_init = [];
for (var i = 0; i <= par_dispos.nmax; i++) {
    data_dispo_adv_init.push({
        day: 0,
        start_time: 0,
	duration: 0,
        off: i
    });
}
var data_dispo_adv_cur = [];
var del_dispo_adv = false;

// preference selection mode
var pref_selection = {
    butw:70,
    buth:30,
    mary:5,
    marx:10,
    choice:{
        data:[],
        w:25,
        h:25
    },
    mode:[{
        desc:"nominal",
        txt:"Normal",
        selected:true,
    },{
        desc:"paint",
        txt:"Sélection",
        selected:false,
    }]
};
for (var i = 0; i <= par_dispos.nmax; i++) {
    pref_selection.choice.data.push({
        val:i,
        // for smile_trans
        off:-2,
        selected:false
    });
}

// number of required and provided availability slots
var required_dispos = -1;
var filled_dispos = -1;

// display only preferences
var pref_only ;

var dim_dispo = {
    height: 0,
    width: 60,
    right: 10,
    plot:0,
    adv_v_margin: 5
};


/*---------------------
  ------- WEEKS -------
  ---------------------*/
var weeks = {
    init_data: null,
    cur_data: null,
    width: 40,
    height: 30,
    x: 0,
    y: -240, //margin.but,  // - TOP BANNER - //
    ndisp: 13,
    fdisp: 0,
    sel: [1],
    rad: 1.2,
    hfac: 0.9,
    wfac: 0.9,
    cont: null
};

/*----------------------
  -------- GRID --------
  ----------------------*/

// one element per labgroup and per slot
// is filtered when bound
var data_mini_slot_grid = [];

// one element per slot
var data_slot_grid = [];

// keys on top or at the bottom of the grid representing the name of
// the labgroup
// (one element per labgroup and per day)
var data_grid_scale_gp = [];


// keys to the left representing the name of the row
//(one element per row and per hour)
var data_grid_scale_row = [];
var data_grid_scale_hour = ["8h-9h25", "9h30-10h55", "11h05-12h30", "14h15-15h40", "15h45-17h10", "17h15-18h40"];


// Garbage parameters
var garbage = {
    start: time_settings.time.day_finish_time,
    duration: 90,
    day: days[days.length-2].ref
};


/*----------------------
  ------- BKNEWS -------
  ----------------------*/

// bknews = breaking news
var bknews = {
    hour_bound:3, // flash info between hour #2 and hour #3
    ratio_height: .55,        // ratio over course height 
    time_height: 60,
    time_margin: 15,
    ratio_margin: .15, // ratio over course height 
    cont: [],
    nb_rows: 0,
};

/*---------------------
  ------- QUOTE -------
  ---------------------*/

var quote = "" ;


/*----------------------
  ------- GROUPS -------
  ----------------------*/

// 2D data about groups (id_promo, group_subname)
var groups = [];


// access to the root of each promo, and to the groups belonging
// to the same line 
var root_gp = []; // indexed by numpromo
var row_gp = []; // indexed by numrow

// set of promo numbers
var set_promos = [];
// set of promo short description
var set_promos_txt = [];
// set of row numbers
var set_rows = [];

// display parameters
var butgp = {
    height: 20,
    width: 30,
    tlx: 640
};
var margin_but = {
    ver: 10,
    hor: 10
};

/*--------------------
  ------ MENUS -------
  --------------------*/
var menus = {
    x: weeks.x + 20,
    y: weeks.y + 25,
    mx: 20,
    dx: 280,
    h: 30,
    sfac: 0.4,
    ifac: 0.7,
    coled: 100,
    colcb: 140
};

var edt_but, edt_message;
// parameters for each checkbox
var ckbox = [];
ckbox["edt-mod"] = {
    i: 0,
    menu: "edt-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};
ckbox["dis-mod"] = {
    i: 1,
    menu: "dis-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};



var context_menu = {
    dispo_hold: false,
    room_tutor_hold: false
};

/*--------------------
   ------ MODULES ------
   --------------------*/
// modules (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var modules = {
    sel: "",
    pl: [],
    pp: [],
    all: [],
    old: []
};

/*--------------------
   ------ ROOMS ------
   --------------------*/
// salles (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var salles = {
    sel: "",
    pl: [],
    pp: [],
    all: []
};

var rooms ;
var rooms_sel = {
    all: [],
    old: []
};

var unavailable_rooms = {} ;


/*---------------------
   ------ TUTORS ------
   --------------------*/

var tutors = {
    // instructors of unscheduled courses
    pp: [],
    // instructors of scheduled courses
    pl: [],
    // all instructors
    all: [],
    old: []
};

// instructors not blurried
var prof_displayed = [];

// display parameters
var but_exit = {
    side: 20,
    mar_side: 3,
    mar_next: 10
};
var sel_popup = {
    type: "",
    x: 640,
    y: -210,
    w: 0,
    h:0,
    groups_w: 0,
    groups_h: 0,
    selw: 60,
    selh: 30,
    selx: 570,
    sely: -200,
    selmy: 8,
    mar_side: 5,
    tlx: 700,
    available: [{type:"group",
                 buttxt: "Groupes",
                 active: false},
                {type: "tutor",
                 buttxt: "Profs",
                 active: false},
                {type:"module",
                 buttxt: "Modules",
                 active: false}
                ],
    get_available: function(t) {
        var ret = this.available.find(function(d) {
            return d.type == t ;
        });
        if (typeof ret === 'undefined') {
            console.log("type unknown");
            return ;
        } else {
            return ret ;
        }
    },
    panels: [], //{type, x, y, w, h, txt}
    but: [],
    active_filter: false
};
if (!cosmo) {
    sel_popup.available.push({type:"room",
                              buttxt: "Salles",
                              active: false});
}
sel_popup.but["tutor"] = {
    h: 30,
    w: 40,
    perline: 5,
    mar_x: 2,
    mar_y: 4,
};
sel_popup.but["room"] = {
    h: 30,
    w: 60,
    perline: 6,
    mar_x: 2,
    mar_y: 4,
};
sel_popup.but["module"] = {
    h: 30,
    w: 40,
    perline: 3,
    mar_x: 2,
    mar_y: 4,
};
sel_popup.available.forEach(function(panel) {
    panel.x = sel_popup.x ;
    panel.y = sel_popup.y ;
}) ;

// has any instructor been fetched?
var first_fetch_prof = true;

// all tutors (to propose changes)
var all_tutors = [] ;

/*--------------------
   ------ SCALE ------
  --------------------*/
// listeners for Horizontal Scaling and Vertical Scaling buttons
var drag_listener_hs, drag_listener_vs;

/*-----------------------
   ------ COURSES -------
  -----------------------*/
// unscheduled curses
var cours_pp = [];
// scheduled curses
var cours_pl = [];
// all curses
var cours = [];

// listener for curses drag and drop 
var dragListener;
var drag_popup ;

// helper for the d&d
var drag = {
    sel: null,
    x: 0,
    y: 0,
    init: 0,
    svg: null,
    svg_w: 0,
    svg_h: 0
};

// course being moved
var pending = {
    init_course: null,
    wanted_course: null,
    time: null,
    pass: {tutor: false,
           room: false,
           core: false},
    force: {tutor: true,
            room: true},
    init_force_pass: function() {
        this.pass.tutor = false;
        this.pass.room = false;
        this.pass.core = false;
        this.force.room = true ;
        this.force.tutor = true ;
    },
    one_try: function() {
        this.force.room = false ;
        this.force.tutor = false ;
    },
    init: function() {
        this.init_course = null ;
        this.wanted_course = null ;
        this.time = null ;
        this.init_force_pass() ;
    },
    fork_course: function(d) {
        this.wanted_course = d ;
        this.init_course = Object.assign({}, d);
    },
    back_init: function(t) {
        Object.assign(this.wanted_course, this.init_course) ;
        this.init() ;
    }
} ;

// stores the courses that has been moved
var cours_bouge = {};

// stores the constraints regarding course types
var constraints ;
var rev_constraints = {};

// scale factor for vertical display: time*factor -> y 
var scale = 1 ;

/*----------------------
  ------- VALIDATE -----
  ----------------------*/

// display parameters
var valid = {
    margin_edt: 50,
    margin_h: 20,
    h: 40,
    w: 210
};

// acknowledgements when availability or courses are changed (ack.edt) ,
// or about the next possible regeneration of the planning (ack.regen)
var ack = {
    more:"",
    // regen infos
    regen: "",
    // for stype
    pref: "",
    status: "OK",
    predefined: {KO: "C'est un échec cuisant. Trouvez un·e responsable d'emploi du temps et faites-lui part de vos problèmes.",
                 OK: "La modification s'est déroulée sans accroc."}
};



/*--------------------
   ------ STYPE ------
  --------------------*/

// display parameters
var did = {
    h: 60,
    w: 15,
    mh: 5,
    mav: 10,
    tlx: 316,
    tly: -180,
    shift_s: 20
};
did.scale = did.h / (time_settings.time.day_finish_time
		     - time_settings.time.lunch_break_finish_time
		     + time_settings.time.lunch_break_start_time
		     - time_settings.time.day_start_time) ;
var stbut = {
    w: 104,
    h: 60
};

/*--------------------
   ------ ALL -------
  --------------------*/

var departments = {
    data: [],
    marh:10,
    topx:sel_popup.selx + sel_popup.selw + 50,
    topy:sel_popup.sely - sel_popup.selh - sel_popup.selmy,
    w:35,
    h:sel_popup.selh
}

// version of the planning
var version;

logged_usr.dispo_all_see = false ;
logged_usr.dispo_all_change = false ;


if ((logged_usr.rights >> 0) % 2 == 1) {
    logged_usr.dispo_all_see = true ;
}
if ((logged_usr.rights >> 1) % 2 == 1) {
    logged_usr.dispo_all_change = true ;
}
    
var user = {nom: logged_usr.nom,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: [],
	    dispo_all_see: false,
	    dispo_all_change: false
	   };

var total_regen = false ;


// 
var entry_cm_settings =
    {type: 'entry',
     w: 100,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 1,
     nlin: 2,
     txt_intro: {'default':"Quoi changer ?"}
    };
var tutor_module_cm_settings =
    {type: 'tutor_module',
     w: 45,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 3,
     nlin: 0,
     txt_intro: {'default':"Profs du module ?"}
    };
var tutor_filters_cm_settings =
    {type: 'tutor_filters',
     w: 120,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 1,
     nlin: 0,
     txt_intro: {'default':"Ordre alphabétique :"}
    };
var tutor_cm_settings =
    {type: 'tutor',
     w: 45,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 3,
     nlin: 4,
     txt_intro: {'default':"Ordre alphabétique :"}
    };
var room_cm_settings =
    [{type: 'room_available',
      txt_intro: {'0':"Aucune salle disponible",
		  '1':"Salle disponible",
		  'default':"Salles disponibles"
		 }
     },
     {type: 'room_available_same_type',
      txt_intro: {'0':"Aucune salle disponible (tout type)",
		  '1':"Salle disponible (tout type)",
		  'default':"Salles disponibles (tout type)"
		 }
     },
     {type: 'room',
      txt_intro: {'0':"Aucune salle",
		  '1':"Salle",
		  'default':"Toutes les salles"
		 }
     }];
for(var l = 0 ; l < room_cm_settings.length ; l++) {
    room_cm_settings[l].w = 45 ;
    room_cm_settings[l].h = 18 ;
    room_cm_settings[l].fs = 10 ;
    room_cm_settings[l].mx = 5 ;
    room_cm_settings[l].my = 3 ;
    room_cm_settings[l].ncol = 3 ;
    room_cm_settings[l].nlin = 0 ;
}
// level=0: the proposed rooms are available and of the same type
//       1: the proposed rooms are available
//       2: all rooms are proposed
var room_cm_level = 0 ;


var salarie_cm_settings =
    {type: 'entry',
     w: 100,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 3,
     nlin: 0,
     txt_intro: {'default':"Qui s'y colle ?"}
    };

// level=0: salaries qui ont le même poste dans la semaine
//       1: tous les salaries
var salarie_cm_level = 0 ;

var room_tutor_change = {
    course: [],    // 1-cell array for d3.js
    proposal: [],
    old_value: "",  
    cur_value: "",
    cm_settings:{},
    top: 30,
    posv: 's',
    posh: 'w'
};

var arrow =
    {right: "→",
     back: "↩"} ;


var is_side_panel_open = false ;
