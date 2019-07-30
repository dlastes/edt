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

// days
var week_days = new WeekDays();
for (var iday in days) {
    week_days.add_day(days[iday]);
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

// remove context menu if click outside
function cancel_cm_adv_preferences(){
    if(ckbox["dis-mod"].cked) {
	if(! context_menu.dispo_hold) {
	    data_dispo_adv_cur = [] ;
	    go_cm_advanced_pref(true);
	}
	context_menu.dispo_hold = false ;
    }
}

// remove context menu if click outside
function cancel_cm_room_tutor_change(){
    if(ckbox["edt-mod"].cked) {
	if(!context_menu.room_tutor_hold) {
	    if (room_tutor_change.course.length > 0) {
		room_tutor_change.course = [] ;
		room_tutor_change.proposal = [] ;
		go_cm_room_tutor_change();
	    }
	}
	context_menu.room_tutor_hold = false ;
    }
}



/*--------------------
   ------ ALL -------
  --------------------*/

// do we have slots
var slot_case = false ; //true ;

// current number of rows
var nbRows;
// last positive number of rows (when filtering by group)
var pos_nbRows = 0;

// maximum number of lab groups among promos
var rootgp_width = 0;
// last positive number of lab groups (when filtering by group)
var pos_rootgp_width = 0;

// different grounds where to plot
var fg, mg, bg, dg, meg, vg, gpg, catg, stg, mog, sag, fig, log, cmpg, cmtg, selg;
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

// Svg 
var svg ;

var dsp_svg =
    {w: 0,
     h: 0,
     margin: {
         top: 0,     // - TOP BANNER - //
         left: 0,
         right: 0,
         bot: 0},
     trans: function() {
         return "translate(" + this.margin.left + "," + this.margin.top + ")" ;
     }
    };

var fun_svg = {
}
/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// 2D array of list [tutor_name][day_reference] -> list of intervals)
var dispos = {};

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

// seed array for advanced preferences (smileys)
var data_dispo_adv_init = [];
for (var i = 0; i <= par_dispos.nmax; i++) {
    data_dispo_adv_init.push({
        day: 0,
        start_time: 0,
	duration: 0,
        off: i
    });
}
// current array for advanced preferences (smileys)
var data_dispo_adv_cur = [];

// number of required and provided availability slots
var required_dispos = -1;
var filled_dispos = -1;

// display only preferences (for typical week)
var pref_only ;

// display parameters for preferences
var dim_dispo = {
    width: 60,
    right: 10,
    // are preferences plotted? 1|0
    plot:0,
    adv_v_margin: 5
};


/*---------------------
  ------- WEEKS -------
  ---------------------*/

var dsp_weeks = {
    visible_weeks: 13,
    width: 40,
    height: 30,
    x: 0,      // top of week banner
    y: -240,   // "
    rad: 1.2,  // ratio for the radius of prev/next week buttons
    hfac: 0.9, // ratio for week selection ellipse
    wfac: 0.9, // ratio for week selection ellipse
    cont: null, // will be initiated in create_clipweek
} ;


var wdw_weeks = new WeeksExcerpt(dsp_weeks.visible_weeks);

// unfortunately cannot use "this", since these functions will
// be passed to d3js
var fun_weeks =
    {trans: function() {
        return "translate(" + dsp_weeks.x + "," + dsp_weeks.y + ")" ;
    },
     sel_x: function (d) {
         return (d + 1 - wdw_weeks.first) * dsp_weeks.width;
     },
     right_sel_x: function() {
         return (wdw_weeks.nb + 1) * dsp_weeks.width ;
     },
     strip_w: function() {
         return (wdw_weeks.nb + 1) * dsp_weeks.width ;
     },
     txt: function(d) {
         return d.semaine;
     },
     rect_x: function(d, i) {
         return (i+1) * dsp_weeks.width - .5 * dsp_weeks.width;
     },
     txt_x: function(d, i) {
         return (i+1) * dsp_weeks.width ;
     },
};

/*----------------------
  -------- GRID --------
  ----------------------*/

// one element per slot
// non-empty iff slot_case
// filled in create_grid_data()
var data_slot_grid = [];

// keys on top or at the bottom of the grid representing the name of
// the labgroup
// (one element per labgroup and per day)
var data_grid_scale_gp = [];


// keys to the left representing the name of the row
// non-empty iff slot_case
//(one element per row and per hour)
var data_grid_scale_row = [];

// Garbage parameters
var garbage = {
    start: time_settings.time.day_finish_time,
    duration: 90,
    day: week_days.day_by_num(week_days.nb_days()-2).ref
};


/*----------------------
  ------- BKNEWS -------
  ----------------------*/

// bknews = breaking news
var bknews = {
    time_height: 60,
    time_margin: 15,
    ratio_margin: .15, // ratio over course height 
    cont: [], // array of bknews contents
    nb_rows: 0, // maximum number of bknews in the same day
};

/*---------------------
  ------- QUOTE -------
  ---------------------*/

var quote = "" ;


/*----------------------
  ------- GROUPS -------
  ----------------------*/

// 2D data about groups [id_promo][group_subname] -> Group
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
    tlx: 640,
    mar_v: 10,
    mar_h: 10
};

/*--------------------
  ------ MENUS -------
  --------------------*/
// course and preference modification menus
var menus = {
    x: dsp_weeks.x + 20,
    y: dsp_weeks.y + 25,
    mx: 20,
    dx: 280,
    h: 30,
    sfac: 0.4,
    ifac: 0.7,
    coled: 100,
    colcb: 140
};

// course modification validation button
var edt_but;
// course modification feedback message
var edt_message;

// parameters for each checkbox
var ckbox = [];
ckbox["edt-mod"] = {
    menu: "edt-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};
ckbox["dis-mod"] = {
    menu: "dis-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};


// for click propagation
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

// tutors (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
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
                 active: false},
                {type:"room",
                 buttxt: "Salles",
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
    edt: "",
    regen: "",
    pref: ""
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
