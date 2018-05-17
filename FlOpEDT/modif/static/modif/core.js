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

var user = {nom: string,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: [],
	   };

var margin = {top: nb, left: nb, right: nb, bot: nb};

var svg = {height: nb, width: nb};

var week = nb ;
var year = nb;

var labgp = {height: nb, width: nb, tot: nb, height_init: nb, width_init: nb};

var dim_dispo = {height:2*labgp.height, width: 60, right: 10, plot:0,
		 adv_v_margin: 5};
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
                 */

/*--------------------
   ------ ALL -------
  --------------------*/

// number of days in the week
var nbPer = 5;

// number of slots within 1 day
var nbSl = 6;

// initial number of promos
var init_nbRows = 2;

// current number of rows
var nbRows;
// last positive number of rows
var pos_nbRows = 0;

// maximum number of lab groups among promos
var rootgp_width = 0;
// last positive number of lab groups
var pos_rootgp_width = 0;

// different grounds where to plot
var fg, mg, bg, dg, meg, vg, gpg, prg, stg, mog, sag, fig, log;
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
    done: false,
    cours_ok: false,
    dispos_ok: false
};
//cours_ok pas très utile


/*---------------------
  ------- DISPOS ------
  ---------------------*/

// 3D array (username,id_day,id_slot)
var dispos = [];

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
        hour: 0,
        off: i
    });
}
var data_dispo_adv_cur = [];
var del_dispo_adv = false;
var dispo_menu_appeared = false;

// number of required and provided availability slots
var required_dispos = -1;
var filled_dispos = -1;

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

// Names of the days
var data_grid_scale_day_init = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven."];
var data_grid_scale_day = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven."];

// Garbage parameters
var garbage = {
    // day: 3,
    // slot: nbSl,
    // cell: {
        day: 3,
        slot: nbSl,
        display: false,
        dispo: false,
        pop: false,
        reason: ""
//    }
};


// bknews = breaking news
var bknews = {
    hour_bound:3, // flash info between hour #2 and hour #3
    ratio_height: .55,        // ratio over course height 
    ratio_margin: .15, // ratio over course height 
    cont: [],
    // [{week: 15, year: 2018, x_beg:1, x_end:2, y:0, fill_col:"forestgreen", strk_col:"black", txt: "13h15, Amphi 2 : Réunion d'info"}, // mouvement UT2J"},
    //  {week: 15, year: 2018, x_beg:1, x_end:2, y:1, fill_col:"forestgreen", strk_col:"black", txt: "Mouvement UT2J"},
    // ],
    nb_rows: 0,
//    2,
};

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


/*--------------------
   ------ MODULES ------
   --------------------*/
// modules (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var modules = {
    sel: "",
    pl: [],
    pp: [],
    all: []
};

/*--------------------
   ------ SALLES ------
   --------------------*/
// salles (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var salles = {
    sel: "",
    pl: [],
    pp: [],
    all: []
};


/*--------------------
   ------ PROFS ------
   --------------------*/

// instructors of unscheduled courses
var profs_pp = [];

// instructors of scheduled courses
var profs_pl = [];

// all instructors
var profs = [];

// instructors not blurried
var prof_displayed = [];

// display parameters
var butpr = {
    height: 30,
    width: 30,
    perline: 12,
    mar_x: 2,
    mar_y: 4,
    tlx: 900
};

// helper variable
// the fetched data is sorted by instructor -> avoid full traversal
var prev_prof;

// has any instructor been fetched?
var first_fetch_prof = true;

/*--------------------
   ------ SCALE ------
  --------------------*/
// listeners for Horizontal Scaling and Vertical Scaling buttons
var drag_listener_hs, drag_listener_vs;

/*--------------------
   ------ COURS -------
  --------------------*/
// fills for courses
var couleurs_fond_texte = [
    ['coral', 'black'],
    ['darkmagenta', 'white'],
    ['deeppink', 'black'],
    ['dodgerblue', 'black'],
    ['goldenrod', 'black'],
    ['lightgreen', 'black'],
    ['mediumslateblue', 'black'],
    ['plum', 'black'],
    ['turquoise', 'black'],
    ['deepskyblue', 'black'],
    ['orange', 'black'],
    ['yellow', 'black'],
    ['peru', 'black'],
    ['springgreen', 'black'],
    ['aquamarine', 'black'],
    ['chocolate', 'white'],
    ['darkkhaki', 'black'],
    ['steelblue', 'white'],
    ['tomato', 'black'],
    ['burlywood', 'black'],
    ['darkred', 'white'],
    ['lightcoral', 'black'],
    ['gold', 'black'],
    ['darkorchid', 'white'],
    ['blanchedalmond', 'black'],
    ['lavender', 'black']
];

// unscheduled curses
var cours_pp = [];
// scheduled curses
var cours_pl = [];
// all curses
var cours = [];

// listener for curses drag and drop 
var dragListener;

// assigns modules to fills
var mod2col = [];

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

/*---------------------
  ------- VALIDER -----
  ---------------------*/

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
    regen: ""
};



/*--------------------
   ------ STYPE ------
  --------------------*/

// display parameters
var did = {
    h: 10,
    w: 15,
    mh: 5,
    mav: 10,
    tlx: 316,
    tly: -180
};
var stbut = {
    w: 104,
    h: 40
};

/*--------------------
   ------ ALL -------
  --------------------*/

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





/*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------  ACTUALISATION -------
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


function go_dispos(quick) {
    if (fetch.dispos_ok) {
        var t, dat, datdi, datsmi;

        if (quick) {
            t = d3.transition()
                .duration(0);
        } else {
            t = d3.transition();
        }

        dat = mg.selectAll(".dispo")
            .data(user.dispos)
            .attr("cursor", ckbox["dis-mod"].cked ? "pointer" : "default");


        datdi = dat
            .enter()
            .append("g")
            .attr("class", "dispo");

        var datdisi = datdi
            .append("g")
            .attr("class", "dispo-si")
            .on("click", apply_change_simple_dispo);


        //dispo-nadv
        //dispo_tot

        datdisi
            .append("rect")
            .attr("class", "dispo-bg")
            .attr("stroke", "black")
            .attr("stroke-width", 1)
            .attr("width", dispo_w)
            .attr("height", 0)
            .attr("x", dispo_x)
            .attr("y", dispo_y)
            .attr("fill", function(d) {
                return smi_fill(d.val / par_dispos.nmax);
            })
            .merge(dat.select(".dispo-bg"))
            .transition(t)
            .attr("width", dispo_w)
            .attr("height", nbRows * labgp.height)
            .attr("x", dispo_x)
            .attr("y", dispo_y)
            .attr("fill", function(d) {
                return smi_fill(d.val / par_dispos.nmax);
            });

        var datex = dat
            .exit();

        datex
            .select(".dispo-bg")
            .transition(t)
            .attr("height", 0);

        datex
            .remove();


        go_smiley(dat, datdisi, t);





        datadvdi = datdi
            .append("g")
            .attr("class", "dispo-a");

        datadvdi
            .merge(dat.select(".dispo-a"))
            .on("click", function(d) {
                if (ckbox["dis-mod"].cked) {
                    if (del_dispo_adv) {
                        del_dispo_adv = false;
                    }
                    dispo_menu_appeared = true;
                    data_dispo_adv_cur = data_dispo_adv_init.map(
                        function(c) {
                            return {
                                day: d.day,
                                hour: d.hour,
                                off: c.off
                            };
                        });
                }
            });


        datadvdi
            .append("rect")
            .attr("stroke", "none")
            .attr("stroke-width", 1)
            .attr("fill", "black")
            .attr("opacity", 0)
            //.attr("fill", function(d){return smi_fill(rc(d));})
            .merge(dat.select(".dispo-a").select("rect"))
            .attr("width", dispo_more_h)
            .attr("height", dispo_more_h)
            .attr("x", dispo_more_x)
            .attr("y", dispo_more_y);
        //	.attr("fill", function(d){return smi_fill(rc(d));});

        datadvdi
            .append("line")
            .attr("stroke-linecap", "butt")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("li", "h")
            .attr("x1", cross_l_x)
            .attr("y1", cross_m_y)
            .attr("x2", cross_r_x)
            .attr("y2", cross_m_y)
            .merge(dat.select(".dispo-a").select("[li=h]"))
            .transition(t)
            .attr("x1", cross_l_x)
            .attr("y1", cross_m_y)
            .attr("x2", cross_r_x)
            .attr("y2", cross_m_y);

        datadvdi
            .append("line")
            .attr("stroke-linecap", "butt")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("li", "v")
            .attr("x1", cross_m_x)
            .attr("y1", cross_t_y)
            .attr("x2", cross_m_x)
            .attr("y2", cross_d_y)
            .merge(dat.select(".dispo-a").select("[li=v]"))
            .transition(t)
            .attr("x1", cross_m_x)
            .attr("y1", cross_t_y)
            .attr("x2", cross_m_x)
            .attr("y2", cross_d_y);

        datadvdi
            .append("circle")
            .attr("fill", "none")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("cx", cross_m_x)
            .attr("cy", cross_m_y)
            .attr("r", par_dispos.rad_cross * smiley.tete)
            .merge(dat.select(".dispo-a").select("circle"))
            .transition(t)
            .attr("cx", cross_m_x)
            .attr("cy", cross_m_y)
            .attr("r", par_dispos.rad_cross * smiley.tete);



        var dis_men_dat = dg
            .selectAll(".dispo-menu")
            .data(data_dispo_adv_cur);

        var dis_men = dis_men_dat
            .enter()
            .append("g")
            .attr("class", "dispo-menu")
            .attr("cursor", "pointer")
            .on("click", function(d) {
                dispos[user.nom][d.day][d.hour] = d.off;
                user.dispos[day_hour_2_1D(d)].val = d.off
            });

        dis_men
            .append("rect")
            .attr("class", "dis-men-bg")
            .merge(dis_men_dat.select(".dis-men-bg"))
            .transition(t)
            .attr("x", dispo_all_x)
            .attr("y", dispo_all_y)
            .attr("width", dispo_all_w)
            .attr("height", dispo_all_h)
            .attr("fill", function(d) {
                return smi_fill(d.off / par_dispos.nmax);
            })
            .attr("stroke", "darkslategrey")
            .attr("stroke-width", 2);

        go_smiley(dis_men_dat, dis_men, t);


        dis_men_dat.exit().remove();




    }
}

function go_smiley(top, mid, t) {
    var datsmi = mid
        .append("g")
        .attr("class", "smiley")
        .attr("stroke-width", 1)
        .attr("transform", smile_trans)
        .attr("stroke", "black");

    datsmi
        .merge(top.select(".smiley"))
        .transition(t)
        .attr("transform", smile_trans)
        .attr("stroke", "black");

    datsmi
        .append("circle")
        .attr("st", "t")
        .merge(top.select("[st=t]"))
        .attr("cx", 0)
        .attr("cy", 0)
        .attr("r", smiley.tete)
        .attr("stroke", function(d) {
            return tete_str(rc(d));
        })
        .attr("fill", function(d) {
            return smi_fill(rc(d));
        });

    datsmi
        .append("circle")
        .attr("st", "od")
        .attr("fill", "none")
        .merge(top.select("[st=od]"))
        .attr("cx", smiley.tete * smiley.oeil_x)
        .attr("cy", smiley.tete * smiley.oeil_y)
        .attr("r", function(d) {
            return oeil_r(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("circle")
        .attr("st", "og")
        .attr("fill", "none")
        .merge(top.select("[st=og]"))
        .attr("cx", -smiley.tete * smiley.oeil_x)
        .attr("cy", smiley.tete * smiley.oeil_y)
        .attr("r", function(d) {
            return oeil_r(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });


    datsmi
        .append("line")
        .attr("st", "sd")
        .merge(top.select("[st=sd]"))
        .attr("x1", function(d) {
            return sourcil_int_x(rc(d));
        })
        .attr("y1", function(d) {
            return sourcil_int_y(rc(d));
        })
        .attr("x2", function(d) {
            return sourcil_ext_x(rc(d));
        })
        .attr("y2", function(d) {
            return sourcil_ext_y(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("line")
        .attr("st", "sg")
        .merge(top.select("[st=sg]"))
        .attr("x1", function(d) {
            return sourcil_intg_x(rc(d));
        })
        .attr("y1", function(d) {
            return sourcil_int_y(rc(d));
        })
        .attr("x2", function(d) {
            return sourcil_extg_x(rc(d));
        })
        .attr("y2", function(d) {
            return sourcil_ext_y(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("rect")
        .attr("st", "si")
        .merge(top.select("[st=si]"))
        .attr("x", -.5 * smiley.rect_w * smiley.tete)
        .attr("y", -.5 * smiley.rect_h * smiley.tete)
        .attr("width", function(d) {
            return interdit_w(rc(d));
        })
        .attr("height", smiley.rect_h * smiley.tete)
        .attr("fill", "white")
        .attr("stroke", "none");

    datsmi
        .append("path")
        .attr("st", "b")
        .merge(top.select("[st=b]"))
        .attr("d", function(d) {
            return smile(rc(d));
        })
        .attr("fill", "none")
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });


}


function create_alarm_dispos() {
    di = dig
        .append("g")
        .attr("text-anchor", "start")
        .attr("class", "disp-info");

    di
        .append("text")
        .attr("class", "disp-required")
        .text(txt_reqDispos);

    di
        .append("text")
        .attr("class", "disp-filled")
        .text(txt_filDispos);
}

function go_alarm_dispos() {

    dig
        .select(".disp-info").select(".disp-required")
        .text(txt_reqDispos)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly + valid.h * 1.5);
    dig
        .select(".disp-info").select(".disp-filled")
        .text(txt_filDispos)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly + valid.h * 1.5 + valid.margin_h);

    if (required_dispos > filled_dispos) {
        dig
            .select(".disp-info").select(".disp-filled")
            .attr("font-weight", "bold").attr("fill", "red");
        dig
            .select(".disp-info").select(".disp-required")
            .attr("font-weight", "bold");
    } else {
        dig
            .select(".disp-info").select(".disp-filled")
            .attr("font-weight", "normal").attr("fill", "black");
        dig
            .select(".disp-info").select(".disp-required")
            .attr("font-weight", "normal");
    }
}





/*---------------------
  ------- WEEKS -------
  ---------------------*/


function go_week(quick) {

    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition()
            .duration(200);
    }

    var sa_wk =
        weeks.cont
        .selectAll(".rec_wk")
        .data(weeks.cur_data, function(d) {
            return d.an + "" + d.semaine;
        });

    sa_wk.exit().transition(t).remove();

    var g_wk = sa_wk
        .enter()
        .append("g")
        .attr("class", "rec_wk");

    g_wk
        .merge(sa_wk)
        .on("click", apply_wk_change);


    g_wk
        .append("rect")
        .attr("y", 0)
        .attr("height", weeks.height)
        .attr("width", weeks.width)
        .attr("x", rect_wk_init_x)
        .merge(sa_wk.select("rect"))
        .transition(t)
        .attr("x", rect_wk_x);

    g_wk
        .append("text")
        .attr("fill", "white")
        .text(rect_wk_txt)
        .attr("y", .5 * weeks.height)
        .attr("x", rect_wk_init_x)
        .merge(sa_wk.select("text"))
        .transition(t)
        .attr("x", function(d, i) {
            return rect_wk_x(d, i) + .5 * weeks.width;
        });

    var wk_sel =
        wg.fg
        .selectAll(".sel_wk")
        .data(weeks.sel)
        .select("ellipse")
        .transition(t)
        .attr("cx", week_sel_x);
    //	.attr("cy",.5*(weeks.hfac-1)*weeks.height);


}
/*----------------------
  -------- GRID --------
  ----------------------*/
function go_grid(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    var grid = bg.selectAll(".gridm")
        .data(data_mini_slot_grid
            .filter(function(d) {
                return d.gp.display;
            }),
            function(d) {
                return d.gp.promo + "," + d.gp.nom + "," + d.day + "," + d.slot;
            });

    grid
        .enter()
        .append("rect")
        .attr("class", "gridm")
        .attr("x", gm_x)
        .attr("y", gm_y)
        .attr("width", 0)
        .merge(grid)
        .transition(t)
        .attr("x", gm_x)
        .attr("y", gm_y)
        .attr("width", labgp.width)
        .attr("height", labgp.height);

    grid.exit()
        .transition(t)
        .attr("width", 0)
        .remove();

    grid = fg.selectAll(".grids")
        .data(data_slot_grid);
    //    grid.transition().duration(100);
    //grid
    var gridg = grid
        .enter()
        .append("g")
        .attr("class", "grids")
        .style("cursor", gs_cursor)
        .on("click", clear_pop);


    gridg
        .append("rect")
        .attr("x", gs_x)
        .attr("y", gs_y)
        .attr("stroke", gs_sc)
        .attr("stroke-width", gs_sw)
        .merge(grid.select("rect"))
        .transition(t)
        .attr("fill-opacity", gs_opacity)
        .attr("x", gs_x)
        .attr("y", gs_y)
        .attr("width", gs_width)
        .attr("height", gs_height)
        .attr("fill", gs_fill);

    grid
	.exit()
	.remove();

    gridg
        .append("text")
        .attr("stroke", "none")
        .attr("font-size", 14)
        .attr("x", function(s) {
            return gs_x(s) + .5 * gs_width(s);
        })
        .attr("y", function(s) {
            return gs_y(s) + .5 * gs_height(s);
        })
        .merge(grid.select("text"))
        .transition(t)
        .attr("x", function(s) {
            return gs_x(s) + .5 * gs_width(s);
        })
        .attr("y", function(s) {
            return gs_y(s) + .5 * gs_height(s);
        })
        .text(gs_txt);


    grid = bg.selectAll(".gridscg")
        .data(data_grid_scale_gp
            .filter(function(d) {
                return d.gp.display;
            }),
            function(d) {
                return d.gp.promo + "," + d.day + "," +
                    d.gp.nom;
            });

    grid
        .enter()
        .append("text")
        .attr("class", "gridscg")
        .attr("x", gscg_x)
        .attr("y", gscg_y)
        .text(gscg_txt)
        .merge(grid)
        .transition(t)
        .attr("x", gscg_x)
        .attr("y", gscg_y);

    grid.exit().remove();


    grid = bg.selectAll(".gridscp")
        .data(data_grid_scale_row
            .filter(function(d) {
                return row_gp[d.row].display;
            }),
            function(d) {
                return d.row + "," + d.slot;
            });

    grid
        .enter()
        .append("text")
        .attr("class", "gridscp")
        .attr("x", gscp_x)
        .attr("y", gscp_y)
        .text(gscp_txt)
        .merge(grid)
        .transition(t)
        .attr("x", gscp_x)
        .attr("y", gscp_y);

    grid.exit().remove();



    bg
        .selectAll(".gridsckd")
        .data(data_grid_scale_day)
        .transition(t)
        .text(gsckd_txt)
        .attr("fill", "darkslateblue")
        .attr("font-size", 22)
        .attr("x", gsckd_x)
        .attr("y", gsckd_y);
    bg
        .selectAll(".gridsckh")
        .data(data_grid_scale_hour)
        .transition(t)
        .attr("x", gsckh_x)
        .attr("y", gsckh_y);



    fg.select(".h-sca").select("rect")
        .transition(t)
        .attr("x", but_sca_h_x())
        .attr("y", but_sca_h_y());
    fg.select(".h-sca").select("path")
        .transition(t)
        .attr("d", but_sca_tri_h(0));

    fg.select(".v-sca").select("rect")
        .transition(t)
        .attr("x", but_sca_v_x())
        .attr("y", but_sca_v_y());
    fg.select(".v-sca").select("path")
        .transition(t)
        .attr("d", but_sca_tri_v(0));



}


function go_bknews(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    fig
	.select(".top")
        .transition(t)
        .attr("x1", 0)
        .attr("y1", bknews_top_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_top_y());

    fig
	.select(".bot")
        .transition(t)
        .attr("x1", 0)
        .attr("y1", bknews_bot_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_bot_y());
    
    var flash = fig.select(".txt-info");

    var fl_all = flash
	.selectAll(".bn-all")
	.data(bknews.cont);
	//       .filter(function(d){
	//     return d.week == weeks.init_data[weeks.sel[0]].semaine
	// 	&& d.year == weeks.init_data[weeks.sel[0]].an ;
	// }));
    //,	      function(d) {return "("+d.x+","+d.y+")" ; } );

    var ffl = fl_all
	.enter()
	.append("g")
	.attr("class", "bn-all");

    ffl
	.append("rect")
	.attr("class", "bn-rec")
	.attr("fill", bknews_row_fill)
	.attr("stroke", bknews_row_fill)
	.attr("stroke-width", 1)
	.attr("y", bknews_row_y)
	.merge(fl_all.select(".bn-rec"))
        .transition(t)
	.attr("x", bknews_row_x)
	.attr("y", bknews_row_y)
	.attr("width", bknews_row_width)
	.attr("height", bknews_row_height);
    
    

    ffl
	.append("text")
	.attr("class", "bn-txt")
	.attr("fill", bknews_row_txt_strk)
	.text(bknews_row_txt)
	.attr("y", bknews_row_txt_y)
	.merge(fl_all.select(".bn-txt"))
        .transition(t)
	.attr("x", bknews_row_txt_x)
	.attr("y", bknews_row_txt_y);

    fl_all.exit().remove();
    
}


/*----------------------
  ------- GROUPS -------
  ----------------------*/
function go_gp_buttons() {
    for (var p = 0; p < set_promos.length; p++) {
        var cont =
            gpg.selectAll(".gp-but-" + set_promos[p] + "P")
            .data(Object.keys(groups[p]).map(function(k) {
                return groups[p][k];
            }));

        var contg = cont
            .enter()
            .append("g")
            .attr("class", "gp-but-" + set_promos[p] + "P")
            //.attr("transform","translate("+gpbutTLX+","+(grid_height()+margin_but.ver)+")")
            .attr("transform", function(gp) {
                return "translate(" + root_gp[gp.promo].butx + "," + root_gp[gp.promo].buty + ")";
            })
            .attr("gpe", function(gp) {
                return gp.nom;
            })
            .attr("promo", function(gp) {
                return gp.promo;
            })
            .on("click", function(gp) {
		apply_gp_display(gp, false, true);
	    });


        contg.append("rect")
            .attr("x", butgp_x)
            .attr("y", butgp_y)
            .attr("width", butgp_width)
            .attr("height", butgp_height)
            .merge(cont.select("rect"))
            .attr("fill", fill_gp_button)
            .attr("stroke-width", 1)
            .attr("stroke", "black");

        contg.append("text")
            .attr("x", butgp_txt_x)
            .attr("y", butgp_txt_y)
            .text(butgp_txt);

        // // CHEAT
        // gpbutTLY += 3*butgp.height + margin_but.ver;
        // gpbutTLX += 0 ; //butgp.width ;
    }

}


/*--------------------
  ------ MENUS -------
  --------------------*/
function go_menus() {

    var init = meg
        .selectAll(".ckline")
        .data(Object.keys(ckbox));


    var ent = init
        .enter()
        .append("g")
        .attr("class", "ckline")
        .on("click", apply_ckbox);



    var cs = ent
        .append("g")
        .attr("class", "ckstat");

    var cd = ent.
    append("g")
        .attr("class", "ckdyn");


    cs
        .append("rect")
        //.attr("x",menus.coled)
        .attr("x", menu_cks_x)
        .attr("y", menu_cks_y)
        .attr("rx", 2)
        .attr("ry", 2)
        .attr("width", menus.sfac * menus.h)
        .attr("height", menus.sfac * menus.h)
        .merge(init.select(".ckstat").select("rect"))
        .attr("stroke", menu_cks_fill)
        .attr("stroke-width", menu_cks_stw);

    cs
        .append("text")
        .attr("x", menu_ck_txt_x)
        .attr("y", menu_ck_txt_y)
        .merge(init.select(".ckstat").select("text"))
        .attr("fill", menu_cks_fill)
        .text(menu_cks_txt);


    cd
        .append("rect")
        .attr("stroke", "none")
        .attr("x", menu_ckd_x)
        .attr("y", menu_ckd_y)
        .attr("width", menus.ifac * menus.sfac * menus.h)
        .attr("height", menus.ifac * menus.sfac * menus.h)
        .merge(init.select(".ckdyn").select("rect"))
        .attr("fill", menu_ckd_fill);


    meg
        .selectAll(".ckline")
        .data(Object.keys(ckbox))
        .attr("cursor", menu_curs);

}


/*--------------------
  ------ MODULES -------
  --------------------*/

function go_modules() {
    var sel_i = mog.property('selectedIndex');
    modules.sel = mog
        .selectAll("option")
        .filter(function(d, i) {
            return i == sel_i;
        })
        .datum();
    go_opac_cours();
}

/*--------------------
  ------ SALLES -------
  --------------------*/

function go_salles() {
    var sel_i = sag.property('selectedIndex');
    salles.sel = sag
        .selectAll("option")
        .filter(function(d, i) {
            return i == sel_i;
        })
        .datum();
    go_opac_cours();
}


/*--------------------
   ------ PROFS ------
  --------------------*/

function go_profs() {

    var profb =
        prg.selectAll(".profs-but")
        .data(profs, function(p) {
            return p;
        })
        .attr("opacity", function(p) {
            return prof_displayed.indexOf(p) > -1 ? 1 : opac;
        });

    go_opac_cours();
}





/*--------------------
   ------ COURS -------
  --------------------*/

function go_cours(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    // var divtip = d3.select("body").append("div")
    // .attr("class", "tooltip")
    // .style("opacity", 0);

    var cg = mg.selectAll(".cours")
        .data(cours.filter(function(d) {
                return groups[d.promo][d.group].display;
            }),
            function(d) {
                return d.id_cours;
            })
        .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default");

    var incg = cg.enter()
        .append("g")
        .attr("class", "cours")
        .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default")
        .on("contextmenu", make_editable)
        .call(dragListener);

    incg
        .append("rect")
        .attr("class", "crect")
        .attr("x", cours_x)
        .attr("y", cours_y)
        .attr("width", 0)
        .merge(cg.select("rect"))
        .attr("fill", function(d) {
	    if (d.id_cours != -1) {
		return mod2col[d.mod][0];
	    }
	    return "red";
        })
        .transition(t)
        .attr("x", cours_x)
        .attr("y", cours_y)
        .attr("width", cours_width)
        .attr("height", cours_height);

    if (ckbox["edt-mod"].cked
	&& logged_usr.dispo_all_see) {
        d3.selectAll("rect.crect").style("fill", function(d) {
            //return mod2col[d.mod][0];
            ////console.log(d);
            ////console.log(dispos);
            try {
                ////console.log(" "+d.prof+" "+d.day+" "+d.slot+" "+dispos[d.prof][d.day][d.slot]);
                lDis = dispos[d.prof][d.day][d.slot];
            } catch (e) {
                lDis = par_dispos.nmax;
            }

            return smi_fill(lDis / par_dispos.nmax);
        })
    } else {
        d3.selectAll("rect.crect").style("fill", function(d) {
	    if (d.id_cours != -1) {
		return mod2col[d.mod][0];
	    }
	    return "red";
        })
    }

    // d3.selectAll("g.cours")
    // .on("mouseover", function(d) {
    //     divtip.transition()
    //         .duration(500)
    //         .style("opacity", .95);
    //     divtip.html(d.prof_full_name + " : "  + d.mod)
    //         .style("left", (d3.event.pageX) + "px")
    //         .style("top", (d3.event.pageY+15) + "px");
    //     })
    // .on("mouseout", function(d) {
    //     divtip.transition()
    //         .duration(200)
    //         .style("opacity", 0);
    // })

    incg
        .append("text")
        .attr("st", "m")
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_top_y)
        .text(cours_txt_top_txt)
        .attr("fill", cours_txt_fill)
        .merge(cg.select("[st=m]"))
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_top_y)

    incg
        .append("text")
        .attr("st", "p")
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_mid_y)
        .text(cours_txt_mid_txt)
        .attr("fill", cours_txt_fill)
        .merge(cg.select("[st=p]"))
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_mid_y)

    incg
        .append("text")
        .attr("st", "r")
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_bot_y)
        .merge(cg.select("[st=r]"))
        .text(cours_txt_bot_txt)
        .attr("fill", cours_txt_fill)
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_bot_y)

    cg.exit()
        //.transition()
        .remove();



}



function make_editable(d) {
    if (ckbox["edt-mod"].cked) {
        //console.log("edi");

        d3.event.preventDefault();

        var p = this; //.parentNode;
        //console.log(this);
        //console.log(p);
        //console.log(d3.select(this).select("rect").attr("x"));
        //console.log(d);

        var del = false;

        var p_el = d3.select(p);

        var frm = dg.append("foreignObject").attr("class", "fo");

        var inp = frm
            .attr("x", cours_x(d) + .4 * cours_width(d))
            .attr("y", cours_y(d) + .6 * labgp.height)
            .attr("width", 50)
            .attr("height", 25)
            .append("xhtml:form")
            .append("input")
            .attr("value", function() {
                // nasty spot to place this call, but here we are sure that the <input> tag is available
                // and is handily pointed at by 'this':

                this.focus();

                return d.room;
            })
            .attr("style", "width: 50px;")
            .on("blur", function() {
                //console.log("blur", this, arguments);

                var txt = inp.node().value;
                //console.log(txt);
                add_bouge(d);
                d.room = txt;

                // Note to self: frm.remove() will remove the entire <g> group! Remember the D3 selection logic!
                //console.log("rembl");
                if (!del) {
                    del = true;
                    dg.selectAll(".fo").remove();
                    go_cours(true);
                }
            })
            .on("keypress", function() {
                //console.log("keypress", this, arguments);

                // IE fix
                if (!d3.event)
                    d3.event = window.event;
                var e = d3.event;
                if (e.keyCode == 13) {
                    if (typeof(e.cancelBubble) !== 'undefined') // IE
                        e.cancelBubble = true;
                    if (e.stopPropagation)
                        e.stopPropagation();
                    e.preventDefault();

                    var txt = inp.node().value;

                    add_bouge(d);
                    d.room = txt;

                    // odd. Should work in Safari, but the debugger crashes on this instead.
                    // Anyway, it SHOULD be here and it doesn't hurt otherwise.
                    //console.log("remkp");
                    if (!del) {
                        del = true;
                        dg.selectAll(".fo").remove();
                        go_cours(true);
                    }
                }

            });

    }
}


function go_opac_cours() {

    if (prof_displayed.length < profs.length || modules.sel != "" || salles.sel != "") {
        // view with opacity filter
        var coursp = mg.selectAll(".cours")
            .data(cours.filter(function(d) {
                    var ret = prof_displayed.indexOf(d.prof) > -1;
                    ret = ret && (modules.sel == "" || modules.sel == d.mod);
                    ret = ret && (salles.sel == "" || salles.sel == d.room);
                    return ret;
                }),
                function(d) {
                    return d.id_cours;
                });

        coursp
            .attr("opacity", 1)
            .select("rect").attr("stroke", 'black');

        coursp
            .exit()
            .attr("opacity", opac)
            .select("rect").attr("stroke", 'none');

    } else {
        // view without opacity filter
        mg
            .selectAll(".cours")
            .attr("opacity", 1)
            .select("rect").attr("stroke", 'none');

    }

}



/*--------------------
   ------ VALIDER ----
  --------------------*/


function go_val_but(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    if (ack.edt != "") {
        edt_message.attr("visibility", "visible");
        edt_message.select("text").text(ack.edt);
    } else {
        edt_message.attr("visibility", "hidden");
    }

}


function go_regen(s) {
    if (s != null) {
	total_regen = false ;
        var txt = "";
        var elements = s.split(/,| /);
        if (elements.length % 2 != 0 && elements.length > 1) {
            //console.log("Aie, pb regen");
            txt = "";
        } else if (elements[0] == 'N') {
            txt = "Pas de (re)génération prévue";
        } else if (elements[0] == 'C') {
	    total_regen = true ;
            if (elements.length > 2 && elements[2] == 'S') {
                txt = "Regénération totale (mineure) le " + elements[1] +
                    "(" + elements[3] + ")";
            } else {
                txt = "Regénération totale le " + elements[1];
            }
        } else if (elements[0] == 'S') {
            txt = "Regénération mineure le " + elements[1];
        }

        ack.regen = txt;

        vg.select(".ack-reg").select("text")
            .text(ack.regen);

    }

    vg.select(".ack-reg").select("text")
        .transition(d3.transition())
        .attr("x", grid_width())
        .attr("y", ack_reg_y());

}


function but_bold() {
    d3
        .select(this)
        .select("rect")
        .attr("stroke-width", 4);
}

function but_back() {
    d3
        .select(this)
        .select("rect")
        .attr("stroke-width", 2);
}



/*--------------------
   ------ ALL -------
  --------------------*/

function go_edt(t) {
    go_grid(t);
    go_cours(t);
    go_profs();
    go_dispos(t);
    go_val_but(t);
    go_bknews(t);
    go_alarm_dispos();
    go_regen(null);
}





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



/*---------------------
  ------- DISPOS ------
  ---------------------*/


function apply_change_simple_dispo(d) {
    if (ckbox["dis-mod"].cked) {
        if (Math.floor(d.val % (par_dispos.nmax / 2)) != 0) {
            d.val = Math.floor(d.val / (par_dispos.nmax / 2)) * par_dispos.nmax / 2;
        }
        d.val = (d.val + par_dispos.nmax / 2) % (3 * par_dispos.nmax / 2);
        dispos[user.nom][d.day][d.hour] = d.val;
        user.dispos[day_hour_2_1D(d)].val = d.val;
        go_dispos(true);
    }
}

/*---------------------
  ------- WEEKS -------
  ---------------------*/
function week_left() {
    if (weeks.fdisp > 0) {
        weeks.fdisp -= 1;
        weeks.cur_data.pop();
        weeks.cur_data.unshift(weeks.init_data[weeks.fdisp]);
    }
    go_week(false);
}

function week_right() {
    if (weeks.fdisp + weeks.ndisp + 2 < weeks.init_data.length) {
        weeks.fdisp += 1;
        weeks.cur_data.splice(0, 1);
        weeks.cur_data.push(weeks.init_data[weeks.fdisp + weeks.ndisp + 1]);
    }
    go_week(false);
}

// Not sure ok even if user is quick (cf fetch_cours)
function apply_wk_change(d, i) { //if(fetch.done) {
    //console.log(i);
    if (i > 0 && i <= weeks.ndisp) {
        weeks.sel[0] = i + weeks.fdisp;
    }
    dispos = [];
    user.dispos = [];
    //profs = [];
    //prof_displayed = [] ;
    fetch.cours_ok = false;
    fetch.dispos_ok = false;


    fetch_cours();

    fetch_bknews(false);

    
    if (ckbox["dis-mod"].cked) {
        fetch_dispos();
    };

    // console.log("go_fetch");
    // console.log(weeks.init_data[weeks.sel[0]]);
    go_week(false);
} //}

/*----------------------
  -------- GRID --------
  ----------------------*/
function clear_pop(gs) {
    if (gs.pop) {
        gs.pop = false;
        gs.display = false;
        gs.reason = "";
        go_grid(false);
    }
}


/*---------------------
  ------- PROFS ------
  ---------------------*/
function apply_pr_display(pr) {
    if (fetch.done) {
	if(logged_usr.dispo_all_change && ckbox["dis-mod"].cked){
	    prof_displayed = [pr] ;
	    user.nom = pr ;
	    create_dispos_user_data() ;
	    go_dispos(true) ;
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

            go_profs();
    }
}



function apply_pr_all() {
    if (fetch.done
	&& (!logged_usr.dispo_all_change || !ckbox["dis-mod"].cked)) {
        prof_displayed = profs.slice(0);
        go_profs();
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

function apply_gp_display(gp, start, button_available) {
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
	if (button_available) {
            go_gp_buttons();
	}
    }
    if (fetch.done) {
        go_edt();
    }
}


function propagate_display_down(gp, b) {
    gp.display = b;
    for (var i = 0; i < gp.children.length; i++) {
        propagate_display_down(groups[gp.promo][gp.children[i]], b);
    }
}

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



/*--------------------
   ------ VALIDER ----
   --------------------*/

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
        go_val_but(true);
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
        go_val_but(true);
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
        go_val_but(true);
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
    go_val_but(true);
}


function dis_change_ack(msg, nbDispos) {
    console.log(msg);
    if (msg.responseText == "OK") {
        ack.edt = "modifications dispos : OK !"
    } else {
        ack.edt = msg.getResponseHeader('reason');
        ack.edt += "\nCall PSE or PRG"
    }
    go_val_but(true);

    filled_dispos = nbDispos;
    go_alarm_dispos();

}






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
        go_dispos(true);
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





           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
------- TRANSFORMATIONS ------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
           \     */


/*------------------------
  ----- BKNEWS ----
  ------------------------*/

function bknews_top_y() {
    return nbRows * labgp.height * bknews.hour_bound ;
}
function bknews_bot_y() {
    return bknews_top_y() +  bknews_h() ;
}
function bknews_h() {
    if (bknews.nb_rows == 0) {
	return 0;
    } else {
	return bknews.nb_rows * bknews_row_height()
	    + 2 * bknews.ratio_margin * labgp.height ;
    }
}

function bknews_row_x(d){
    return (d.x_beg * (rootgp_width * labgp.width
		       + dim_dispo.plot * (dim_dispo.width + dim_dispo.right))) ;
}
function bknews_row_y(d){
    return bknews_top_y() + bknews.ratio_margin * labgp.height
	+ d.y * bknews.ratio_height * labgp.height ;
}
function bknews_row_fill(d){
    return d.fill_color ;
}
function bknews_row_width(d){
    return ((d.x_end - d.x_beg) * (rootgp_width * labgp.width
		       + dim_dispo.plot * (dim_dispo.width + dim_dispo.right))) ;
}
function bknews_row_height(d){
    return bknews.ratio_height * labgp.height ;
}
function bknews_row_txt(d){
    return d.txt ;
}
function bknews_row_txt_x(d){
    return bknews_row_x(d) + .5 * bknews_row_width(d) ;
}
function bknews_row_txt_y(d){
    return bknews_row_y(d) + .5 * bknews_row_height(d);
}
function bknews_row_txt_strk(d){
    return d.strk_color ;
}


/*---------------------
  ------- ALL ------
  ---------------------*/

function svg_height() {
    //    return margin.top + ack_reg_y() + 4*margin.bot ;
    return margin.top + grid_height() + labgp.height * nbRows + margin.bot ;
}

function svg_width() {
    //    return margin.top + ack_reg_y() + 4*margin.bot ;
    return margin.left + Math.max(
        // max x of prof buttons
        butpr.tlx + butpr_x(null, butpr.perline - 2) + butpr.width + butpr.mar_x,
        // max x of the edt
        rootgp_width * nbPer * labgp.width + margin.right) ;
}


/*---------------------
  ------- DISPOS ------
  ---------------------*/
function day_hour_2_1D(d) {
    return d.day * nbSl + d.hour;
    //d.day<4?d.day*nbSl+d.hour:d.day*nbSl+d.hour-3;
}


function dispo_x(d) {
    return d.day * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        rootgp_width * labgp.width;
}

function dispo_y(d) {
    var ret = d.hour * nbRows * (labgp.height);
    if (d.hour >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function dispo_w(d) {
    return dim_dispo.plot * dim_dispo.width;
}

function dispo_short_fill(d) {
    var col = "green";
    if (dispos[user.nom][d.day][d.hour] == 4) {
        col = "orange";
    } else if (dispos[user.nom][d.day][d.hour] == 0) {
        col = "red";
    }
    return col;
}


function trans_dispo(d) {
    return "matrix(" +
        dim_dispo.plot +
        ",0,0,1," +
        dispo_x(d) +
        "," +
        dispo_y(d) +
        ")";
}


function dispo_more_h(d) {
    return .25 * nbRows * labgp.height;
}

function dispo_more_y(d) {
    return dispo_y(d) + nbRows * labgp.height - dispo_more_h(d);
}

function dispo_more_x(d) {
    return dispo_x(d) + dispo_w(d) - dispo_more_h(d);
}

function dispo_all_x(d) {
    return dispo_more_x(d) + dispo_more_h(d) -
        par_dispos.adv_red * dispo_w(d);
}

function dispo_all_h(d) {
    return 2 * dim_dispo.adv_v_margin + 2 * smiley.tete;
}

function dispo_all_y(d) {
    return dispo_more_y(d) + d.off * dispo_all_h(d);
}

function dispo_all_w(d) {
    return par_dispos.adv_red * dispo_w(d);
}


function cross_l_x(d) {
    return cross_m_x(d) - par_dispos.red_cross * smiley.tete;
}

function cross_r_x(d) {
    return cross_m_x(d) + par_dispos.red_cross * smiley.tete;
}

function cross_m_x(d) {
    return dispo_x(d) + dispo_w(d) - 1.7 * par_dispos.rad_cross * smiley.tete;
}

function cross_t_y(d) {
    return cross_m_y(d) - par_dispos.red_cross * smiley.tete;
}

function cross_m_y(d) {
    return dispo_more_y(d) + .5 * dispo_more_h(d);
}

function cross_d_y(d) {
    return cross_m_y(d) + par_dispos.red_cross * smiley.tete;
}


function txt_reqDispos() {
    var ret = "";
    if (required_dispos > 0) {
        ret += "Dispos souhaitées : " + required_dispos + " créneaux."
    } else if (required_dispos == 0) {
        ret += "Vous n'intervenez pas cette semaine.";
    }
    return ret;
}

function txt_filDispos() {
    var ret = "";
    if (required_dispos > 0) {
        if (filled_dispos < required_dispos) {
            ret += "Vous en avez " + filled_dispos + ". Merci d'en rajouter.";
        } else {
            ret += "Vous en proposez " + filled_dispos + ". C'est parfait.";
        }
    } else if (required_dispos == 0) {
        //ret += "Pas de problème." // pas de cours => pas de message ;-) 
    }
    return ret;
}



/*---------------------
  ------- SMILEY -------
  ---------------------*/


//ratio content
function rc(d) {
    return d.off == -1 ? dispos[user.nom][d.day][d.hour] / par_dispos.nmax : d.off / par_dispos.nmax;
}


function oeil_r(d) {
    return smiley.tete * (smiley.oeil_min + d * (smiley.oeil_max - smiley.oeil_min));
}

function sourcil_ext_x(d) {
    return smiley.tete * (smiley.oeil_x + d * smiley.sourcil);
}

function sourcil_int_x(d) {
    return smiley.tete * (smiley.oeil_x - (1 - d) * smiley.sourcil);
}

function sourcil_ext_y(d) {
    return smiley.tete * (smiley.oeil_y - (1 - d) * smiley.sourcil);
}

function sourcil_int_y(d) {
    return smiley.tete * (smiley.oeil_y - d * smiley.sourcil);
}

function sourcil_extg_x(d) {
    return -smiley.tete * ((smiley.oeil_x + d * smiley.sourcil));
}

function sourcil_intg_x(d) {
    return -smiley.tete * ((smiley.oeil_x - (1 - d) * smiley.sourcil));
}

function smile(d) {
    return "M" +
        (-smiley.tete * smiley.bouche_x) + " " + smile_coin_y(d) + " Q0 " +
        (smiley.tete * (2 * smiley.bouche_haut_y - smiley.bouche_bas_y +
            3 * d * (smiley.bouche_bas_y - smiley.bouche_haut_y))) + " " +
        (smiley.tete * smiley.bouche_x) + " " + smile_coin_y(d);
}


function smile_coin_y(d) {
    return smiley.tete * (smiley.bouche_bas_y +
        d * (smiley.bouche_haut_y - smiley.bouche_bas_y));
}

function smi_fill(d) {
    if (d <= .5) {
        return "rgb(" +
            100 + "%," +
            2 * d * smiley.mid_o_v + "%," +
            0 + "%)";
    } else {
        return "rgb(" +
            200 * (1 - d) + "%," +
            ((smiley.min_v - smiley.mid_y_v) * (-1 + 2 * d) + smiley.mid_y_v) + "%," +
            0 + "%)";
    }
}

function tete_str(d) {
    return d == 0 ? "white" : "black";
}

function trait_vis_strw(d) {
    return d == 0 ? 0 : 1;
}

function interdit_w(d) {
    return d == 0 ? smiley.rect_w * smiley.tete : 0;
}

function smile_trans(d) {
    if (d.off == -1) {
        return "translate(" +
            (dispo_x(d) + .5 * dim_dispo.width) + "," +
            (dispo_y(d) + .5 * nbRows * labgp.height) + ")";
    } else {
        return "translate(" +
            (dispo_x(d) + (1 - .5 * par_dispos.adv_red) * dispo_w(d)) + "," +
            (dispo_all_y(d) + smiley.tete + dim_dispo.adv_v_margin) + ")";
    }
}


/*---------------------
  ------- WEEKS -------
  ---------------------*/
function rect_wk_txt(d) {
    return d.semaine;
}

function rect_wk_x(d, i) {
    return i * weeks.width - .5 * weeks.width;
}

function rect_wk_init_x(d, i) {
    if (i == 0) {
        return rect_wk_x(0, -1);
    } else if (i == weeks.ndisp + 1) {
        return rect_wk_x(0, weeks.ndisp + 2);
    } else {
        return rect_wk_x(0, i);
    }
}

function week_sel_x(d) {
    return (d - weeks.fdisp) * weeks.width;
}


/*----------------------
  -------- GRID --------
  ----------------------*/
function gm_x(datum) {
    return datum.day * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        datum.gp.x * labgp.width;
}

function gm_y(datum) {
    var daty = row_gp[root_gp[datum.gp.promo].row].y ;
    var ret = (datum.slot * nbRows + daty) * (labgp.height);
    if (datum.slot >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function gs_x(datum) {
    return datum.day * (rootgp_width * labgp.width +
        dim_dispo.plot * (dim_dispo.width + dim_dispo.right));
}

function gs_y(datum) {
    var ret = (datum.slot * nbRows) * (labgp.height) ;
    if (datum.slot >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function gs_width(d) {
    return rootgp_width * labgp.width;
}

function gs_height(d) {
    return labgp.height * nbRows;
}

function gs_fill(d) {
    if (d.display || d.pop) {
        return d.dispo ? "green" : "red";
    } else {
        return "none";
    }
}

function gs_opacity(d) {
    return d.pop ? 1 : .5;
}

function gs_cursor(d) {
    return d.pop ? "pointer" : "default";
}

function gs_txt(s) {
    return s.pop ? s.reason : "";
}

function gs_sw(d) {
    //    return is_free(d.day,d.slot)&&d.slot<5?0:2;
    return 2;
}

function gs_sc(d) {
    //    return d.day==3&&d.slot==5?"red":"black";
    return d.slot < nbSl ? "black" : "red";
}


function gscg_x(datum) {
    // hack for LP
    var hack = 0;
    if (datum.gp.nom == "fakeLP1") {
        hack = .5 * labgp.width;
    }
    return datum.day * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        datum.gp.x * labgp.width +
        .5 * labgp.width +
        hack;
}

function gscg_y(datum) {
    if (datum.gp.promo == 0) {
        return -.25 * labgp.height_init;
    } else {
        // if (datum.day == 3) {
        //     return .5 * grid_height() + .25 * labgp.height_init;
        // }
        return grid_height() + .25 * labgp.height_init;
    }
}

function gscg_txt(datum) {
    if (datum.gp.nom == "fakeLP1") {
        return "LP";
    } else if (datum.gp.nom == "fakeLP2") {
        return "";
    } else {
        return datum.gp.nom;
    }
}

function gscp_x(datum) {
    return -.7 * labgp.width_init;
}

function gscp_y(datum) {
    var ret = (datum.slot * nbRows + row_gp[datum.row].y) * (labgp.height) + .5 * labgp.height;
    if (datum.slot >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;

}

function gscp_txt(d) {
    return d.name;
}

function gsckd_x(datum, i) {
    return i * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        rootgp_width * labgp.width * .5;
}

function gsckd_y(datum) {
    return -.75 * labgp.height_init;
}

function gsckd_txt(d) {
    return d;
}

function gsckh_x(datum) {
    return grid_width() + 5 ;//.25 * labgp.width;
}

function gsckh_y(datum, i) {
    var ret = (i + .5) * nbRows * (labgp.height);
    if (i >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function gsckh_txt(d) {
    return d;
}

/*
function gsclb_y() {
    return nbRows * labgp.height * .5 * nbSl;
}
*/

function grid_height() {
    return nbSl * labgp.height * nbRows + bknews_h();
}

function nb_vert_labgp_in_grid() {
    var tot_labgp =  bknews.nb_rows * bknews.ratio_height + nbRows * nbSl;
    if (bknews.nb_rows != 0) {
	tot_labgp += 2 * bknews.ratio_margin ;
    }
    return tot_labgp ;
}

function labgp_from_grid_height(gh) {
    return gh / nb_vert_labgp_in_grid() ;
}




function grid_width() {
    return (rootgp_width * labgp.width +
        dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) * nbPer;
}





/*----------------------
  ------- GROUPS -------
  ----------------------*/
function butgp_x(gp) {
    return gp.x * butgp.width;
}

function butgp_y(gp) {
    return gp.by * butgp.height;
}

function butgp_width(gp) {
    return gp.width * butgp.width;
}

function butgp_height(gp) {
    return butgp.height * gp.buth;
}

function butgp_txt_x(gp) {
    return butgp_x(gp) + 0.5 * butgp_width(gp);
}

function butgp_txt_y(gp) {
    return butgp_y(gp) + 0.5 * butgp_height(gp)
}

function butgp_txt(gp) {
    if (gp.nom.slice(0, 4) == "fake") {
        return "";
    } else {
        if (gp.nom != "P") {
            if (gp.nom == "23") {
                return "2 & 3";
            }
            return gp.nom;
        } else {
            if (gp.promo == 0) {
                return "Groupes prem. an.";
            } else {
                return "Groupes deux. an.";
            }
        }
    }
}

function fill_gp_button(gp) {
    return (is_no_hidden_grp ? "#999999" : (gp.display ? "forestgreen" : "firebrick"));
}

/*--------------------
  ------ MENUS -------
  --------------------*/

function menu_cks_y(dk, i) {
    return menus.h - .5 * menus.h * menus.sfac - 10;
}

function menu_cks_x(dk, i) {
    return menus.dx * i + menus.coled;
}

function menu_ckd_y(dk, i) {
    return menus.h - .5 * menus.h * menus.sfac * menus.ifac - 10;
}

function menu_ckd_x(dk, i) {
    return menus.dx * i + menus.coled + 0.5 * (1 - menus.ifac) * menus.sfac * menus.h;
}



function menu_ckd_fill(dk) {
    var ret = "none";
    if (ckbox[dk].disp &&
        ckbox[dk].cked) {
        if (ckbox[dk].en) {
            ret = "black";
        } else {
            ret = "grey";
        }
    }
    return ret;
}

function menu_ck_txt_x(dk, i) {
    return menus.dx * i + menus.coled + menus.sfac * menus.h + menus.mx;
}

function menu_ck_txt_y(dk, i) {
    return menus.h - 10;
}

function menu_cks_stw(dk) {
    return ckbox[dk].disp ? 2 : 0;
}

function menu_cks_fill(dk) {
    return ckbox[dk].en ? "black" : "grey";
}

function menu_cks_txt(dk) {
    return ckbox[dk].disp ? ckbox[dk].txt : "";
}

function menu_curs(dk) {
    return ckbox[dk].en ? "pointer" : "default";
}


/*--------------------
  ------ PROFS -------
  --------------------*/
function butpr_x(p, i) {
    return ((i + 1) % butpr.perline) * (butpr.width + butpr.mar_x);
}

function butpr_y(p, i) {
    return Math.floor((i + 1) / butpr.perline) * (butpr.height + butpr.mar_y);
}

function butpr_txt_x(p, i) {
    return butpr_x(p, i) + .5 * butpr.width;
}

function butpr_txt_y(p, i) {
    return butpr_y(p, i) + .5 * butpr.height;
}
/*
function butpr_sw(p) {
    return p==user.nom?4:1;
}
function butpr_col(p) {
    return p==user.nom?"darkorchid":"steelblue";
}
*/
function butpr_class(p) {
    return p == user.nom ? "profs-but-me" : "profs-but-others";
}


/*--------------------
  ------ COURS -------
  --------------------*/
function cours_x(c) {
    return c.day * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        groups[c.promo][c.group].x * labgp.width;
}

function cours_y(c) {
    var ret = (c.slot * nbRows + row_gp[root_gp[c.promo].row].y) * (labgp.height);
    if (c.slot >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function cours_width(c) {
    var gp = groups[c.promo][c.group];
    return (gp.maxx - gp.x) * labgp.width;
}

function cours_height(c) {
    return labgp.height;
}

function cours_txt_x(c) {
    return cours_x(c) + .5 * cours_width(c);
}
function cours_txt_fill(c) {
    if (c.id_cours != -1) {
	return mod2col[c.mod][1];
    }
    return "black";
}
function cours_txt_top_y(c) {
    return cours_y(c) + .25 * labgp.height;
}
function cours_txt_top_txt(c) {
    return c.mod;
}
function cours_txt_mid_y(c) {
    return cours_y(c) + .5 * labgp.height;
}
function cours_txt_mid_txt(c) {
    return c.prof;
}
function cours_txt_bot_y(c) {
    return cours_y(c) + .75 * labgp.height;
}
function cours_txt_bot_txt(c) {
    return c.room;
}



/*--------------------
   ------ SCALE -------
  --------------------*/

function but_sca_h_mid_x() {
    return grid_width();
}

function but_sca_h_x() {
    return but_sca_h_mid_x();
}

function but_sca_h_y() {
    return .5 * grid_height() - .5 * but_sca_long();
}

function but_sca_thick() {
    return .5 * labgp.width_init;
}

function but_sca_long() {
    return 1.2 * labgp.height_init;
}

function but_sca_v_x() {
    return .5 * but_sca_h_mid_x() - .5 * but_sca_long();
}

function but_sca_v_y() {
    return grid_height();
}

function but_sca_tri_h(add) {
    var midx, midy, thick, lon;
    midx = but_sca_h_mid_x();
    midy = .5 * grid_height();
    thick = but_sca_thick();
    lon = but_sca_long();
    return "M" +
        (add + midx + .3 * thick) + " " +
        (midy - .2 * lon) + " L" +
        (add + midx + .7 * thick) + " " +
        (midy) + " L" +
        (add + midx + .3 * thick) + " " +
        (midy + .2 * lon) + " Z";
}

function but_sca_tri_v(add) {
    var midx, midy, thick, lon;
    midx = .5 * but_sca_h_mid_x();
    midy = grid_height();
    thick = but_sca_thick();
    lon = but_sca_long();

    return "M" +
        (midx + .2 * lon) + " " +
        (add + midy + .3 * thick) + " L" +
        (midx) + " " +
        (add + midy + .7 * thick) + " L" +
        (midx - .2 * lon) + " " +
        (add + midy + .3 * thick) + " Z";
}



/*--------------------
   ------ STYPE ------
  --------------------*/
function dispot_x(d) {
    return d.day * (did.w + did.mh);
}

function dispot_y(d) {
    return valid.h * 1.25 + d.hour * did.h;
}

function dispot_w(d) {
    return did.w;
}

function dispot_h(d) {
    return did.h;
}

function dispot_more_h(d) {
    return .25 * did.h;
}

function dispot_more_y(d) {
    return dispot_y(d) + dispot_h(d) - dispot_more_h(d);
}

function dispot_more_x(d) {
    return dispot_x(d) + dispot_w(d) - dispot_more_h(d);
}

function dispot_all_x(d) {
    return dispot_more_x(d) + dispot_more_h(d) -
        par_dispos.adv_red * dispot_w(d);
}

function dispot_all_h(d) {
    return 2 * did.mav + 2 * smiley.tete;
}

function dispot_all_y(d) {
    return dispot_more_y(d) + d.off * dispot_all_h(d);
}

function dispot_all_w(d) {
    return par_dispos.adv_red * dispot_w(d);
}

function gsclbt_y() {
    return valid.h * 1.25 + did.h * .5 * nbSl;
}

function gsclbt_x() {
    return (did.w + did.mh) * nbPer - did.mh;
}

function dispot_but_x() {
    return did.tlx + nbPer * (did.w + did.mh) + did.mh;
}

function dispot_but_y(but) {
    var ret = did.tly + valid.h * 1.25;
    if (but != "app") {
        ret += did.mav;
    }
    return ret;
}

function dispot_but_txt_x() {
    return dispot_but_x() + .5 * stbut.w;
}

function dispot_but_txt_y(but) {
    return dispot_but_y(but) + .5 * stbut.h;
}


function st_but_ptr() {
    if (ckbox["dis-mod"].cked) {
        return "pointer";
    } else {
        return "default";
    }
}

function st_but_bold() {
    if (ckbox["dis-mod"].cked) {
        d3
            .select(this)
            .select("rect")
            .attr("stroke-width", 4);
    }
}

function st_but_back() {
    d3
        .select(this)
        .select("rect")
        .attr("stroke-width", 2);
}


/*---------------------
  ------- VALIDER -----
  ---------------------*/

function ack_reg_y() {
    return grid_height()  + 1.5 *  labgp.height;
}



/*--------------------
   ------ ALL -------
  --------------------*/

function classic_x(d){ return d.x ; }
function classic_y(d){ return d.y ; }
function classic_w(d){ return d.w ; }
function classic_h(d){ return d.h ; }
function classic_txt_x(d) { return classic_x(d) + .5*classic_w(d) ;}
function classic_txt_y(d) { return classic_y(d) + .5*classic_h(d) ;}
function classic_txt(d){ return d.txt ; }




/*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
------    ONLY  ONCE    ------ 
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */




/*----------------------
  -------   SVG  -------
  ----------------------*/



function create_general_svg(light) {
    var tot;

    if (light) {
        tot = d3.select("body");
    } else {
        tot = d3.select("body").append("div");

        mog = tot
            .append("div")
            .attr("id", "div-mod")
            .text("Module ")
            .append("select")
            .attr("id", "dd-mod")
            .on("change", go_modules);

        sag = tot
            .append("div")
            .attr("id", "div-sal")
            .text("Salle ")
            .append("select")
            .attr("id", "dd-sal")
            .on("change", go_salles);


    }

    svg_cont = tot
        .append("svg")
        .attr("width", svg.width)
        .attr("height", svg.height)
        .attr("id", "edt-main")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    create_layouts(svg_cont, light);

    // var divtip = d3.select("body").append("div")
    // 	.attr("class", "tooltip")
    // 	.style("opacity", 0);

}




function create_layouts(svg_cont, light) {
    // menus ground
    meg = svg_cont.append("g")
        .attr("id", "lay-meg");

    // weeks ground
    wg.upper = svg_cont.append("g")
        .attr("id", "lay-wg");
    wg.bg = wg.upper.append("g")
        .attr("id", "wg-bg");
    wg.fg = wg.upper.append("g")
        .attr("id", "wg-fg");

    // groupes ground
    gpg = svg_cont.append("g")
        .attr("id", "lay-gpg");

    // profs ground
    prg = svg_cont.append("g")
        .attr("id", "lay-prg");

    // module ground
    //  mog = d3.select("body").select("select")
    // svg_cont.append("g")
    // 	.attr("id","lay-mog")
    // 	.attr("transform","translate("+modules.x+","+modules.y+")")
    // 	.append("foreignObject")
    // 	.append("xhtml:select")
    // 	.attr("id","dd-mod")
    //	.on("change",go_modules);


    if (!light) {
        //console.log(modules.x);
        //console.log(d3.select("svg").attr("width"));

        $("#div-mod").css("width", modules.width);
        $("#div-mod").css({
            position: "relative",
            left: modules.x,
            top: modules.y
        });
        $("#div-mod").css("height", modules.height);

        $("#div-sal").css("width", salles.width);
        $("#div-sal").css({
            position: "relative",
            left: salles.x,
            top: salles.y
        });
        $("#div-sal").css("height", salles.height);

    }



    // semaine type ground
    stg = svg_cont.append("g")
        .attr("id", "lay-stg");


    // dispos info ground
    dig = svg_cont.append("g")
        .attr("id", "lay-dg");


    // valider
    vg = svg_cont.append("g")
        .attr("id", "lay-vg");

    /*vg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "pink");*/

    // background, middleground, foreground, dragground
    var edtg = svg_cont.append("g")
        .attr("id", "lay-edtg");
    bg = edtg.append("g")
        .attr("id", "lay-bg");
    mg = edtg.append("g")
        .attr("id", "lay-mg");
    fig = edtg.append("g")
        .attr("id", "lay-fig");
    fg = edtg.append("g")
        .attr("id", "lay-fg");

    // logo ground
    log = edtg.append("g")
        .attr("id", "lay-log");

    // drag ground
    dg = svg_cont.append("g")
        .attr("id", "lay-dg");


}




/*----------------------
  -------   DISPOS  -------
  ----------------------*/



/*---------------------
  ------- WEEKS -------
  ---------------------*/



// PRE: semaine_init, week_init, weeks.init_data
function find_week(week_list) {
    var i, up;
    i = 0;
    up = false;
    while (i < week_list.length && !up) {
        if (an_init < week_list[i].an ||
            (an_init == week_list[i].an &&
                semaine_init < week_list[i].semaine)) {
            up = true;
        } else {
            i++;
        }
    }
    if (!up) {
        i = 0;
    }
    return i;
}




function create_clipweek() {

    weeks.init_data = semaine_an_list;

    var min = weeks.init_data[0];
    var max = weeks.init_data[weeks.init_data.length - 1];

    weeks.ndisp = Math.min(weeks.ndisp, weeks.init_data.length);

    weeks.init_data.push({
        an: max.an,
        semaine: max.semaine + 1
    });
    weeks.init_data.unshift({
        an: min.an,
        semaine: min.semaine - 1
    });

    var fw = find_week(weeks.init_data);
    fw = Math.max(
        Math.min(fw - 2,
		 weeks.init_data.length - 1 - (weeks.ndisp + 1)),
        0);

    weeks.cur_data = weeks.init_data.slice(fw,
        fw + weeks.ndisp + 2);

    weeks.fdisp = fw;
    
    weeks.sel[0] =  fw + find_week(weeks.cur_data) - 1 ;


    wg.upper
        .attr("transform", "translate(" + weeks.x + "," + weeks.y + ")");


    wg.fg
        .selectAll(".sel_wk")
        .data(weeks.sel)
        .enter()
        .append("g")
        .attr("class", "sel_wk")
        .attr("clip-path", "url(#clipwk)")
        .attr("pointer-events", "none")
        .append("ellipse")
        .attr("cx", week_sel_x)
        .attr("cy", .5 * weeks.height)
        .attr("rx", .5 * weeks.wfac * weeks.width)
        .attr("ry", .5 * weeks.hfac * weeks.height);



    var but =
        wg.fg
        .append("g")
        .attr("class", "cir_wk")
        .on("click", week_left);


    but
        .append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("cx", 0)
        .attr("cy", .5 * weeks.height)
        .attr("r", weeks.rad * .5 * weeks.height);

    but
        .append("text")
        .attr("fill", "white")
        .attr("x", 0)
        .attr("y", .5 * weeks.height)
        .text("<");


    but =
        wg.fg
        .append("g")
        .attr("class", "cir_wk")
        .on("click", week_right);

    but
        .append("circle")
        .attr("stroke", "white")
        .attr("stroke-width", 1)
        .attr("cx", (weeks.ndisp + 1) * weeks.width)
        .attr("cy", .5 * weeks.height)
        .attr("r", weeks.rad * .5 * weeks.height)

    but
        .append("text")
        .attr("fill", "white")
        .attr("x", (weeks.ndisp + 1) * weeks.width)
        .attr("y", .5 * weeks.height)
        .text(">");


    wg.bg
        .append("rect")
        .attr("class", "cir_wk")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", (weeks.ndisp + 1) * weeks.width)
        .attr("height", weeks.height);

    wg.bg
        .append("g")
        .append("clipPath")
        .attr("id", "clipwk")
        .append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("height", weeks.height)
        .attr("width", (weeks.ndisp + 1) * weeks.width);

    weeks.cont = wg.bg
        .append("g")
        .attr("clip-path", "url(#clipwk)");


    go_week(true);
}





/*----------------------
  -------- GRID --------
  ----------------------*/


function create_bknews() {
    var flash = fig
	.append("g")
	.attr("class", "flashinfo");


    flash
	.append("line")
	.attr("class","bot")
        .attr("stroke", "black")
        .attr("stroke-width", 4)
        .attr("x1", 0)
        .attr("y1", bknews_bot_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_bot_y());

    flash
	.append("line")
	.attr("class","top")
        .attr("stroke", "black")
        .attr("stroke-width", 4)
        .attr("x1", 0)
        .attr("y1", bknews_top_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_top_y());

    var fl_txt = flash
	.append("g")
	.attr("class","txt-info");


    
}

// PRE: groups
function create_edt_grid() {
    create_grid_data();
    //go_grid(false);
}



function add_garbage(){
    data_slot_grid.push(garbage);
}
function remove_garbage(){
    var found = false ;
    var i  = 0 ;
    while(!found && i < data_slot_grid.length){
	if (data_slot_grid[i].day == garbage.day
	    && data_slot_grid[i].slot == garbage.slot) {
	    console.log('found');
	    found = true ;
	    data_slot_grid.splice(i,1);
	}
	i += 1 ;
    }
}


function create_grid_data() {
    for (var j = 0; j < nbPer; j++) {
        for (var s = 0; s < nbSl; s++) {
            var gs = {
                day: j,
                slot: s,
                display: false,
                dispo: false,
                pop: false,
                reason: ""
            };
            data_slot_grid.push(gs);
        }
    }

    for (var p = 0; p < set_promos.length; p++) {
        compute_promo_leaves(root_gp[p].gp);
    }


    for (var s = 0; s < nbSl; s++) {
        for (var r = 0; r < set_rows.length; r++) {
            var gscp = {
                row: r,
                slot: s,
                name: set_promos[row_gp[r].promos[0]] + "A"
            };
            for (var p = 1; p < row_gp[r].promos.length; p++) {
                gscp.name += "|";
                if (set_promos[row_gp[r].promos[p]] == 3) {
                    gscp.name += "LP";
                } else {
                    gscp.name += set_promos[row_gp[r].promos[p]] + "A";
                }
            }
            data_grid_scale_row.push(gscp);
        }
    }
    create_dh_keys();
}



function create_dh_keys() {
    bg
        .selectAll(".gridsckd")
        .data(data_grid_scale_day)
        .enter()
        .append("text")
        .attr("class", "gridsckd")
        .attr("x", gsckd_x)
        .attr("y", gsckd_y)
        .attr("font-size", 13)
        .attr("font-weight", "bold")
        .text(gsckd_txt);

    bg
        .selectAll(".gridsckh")
        .data(data_grid_scale_hour)
        .enter()
        .append("text")
        .attr("class", "gridsckh")
        .attr("x", gsckh_x)
        .attr("y", gsckh_y)
        .text(gsckh_txt);


}



/*----------------------
  -------- SCALE -------
  ----------------------*/

function create_but_scale() {
    def_drag_sca();

    var grp = fg
        .append("g")
        .attr("class", "h-sca")
        .attr("cursor", "pointer")
        .call(drag_listener_hs);

    grp
        .append("rect")
        .attr("fill", "darkslategrey")
        .attr("x", but_sca_h_x())
        .attr("y", but_sca_h_y())
        .attr("width", but_sca_thick())
        .attr("height", but_sca_long());

    grp
        .append("path")
        .attr("d", but_sca_tri_h(0))
        .attr("stroke", "white")
        .attr("fill", "white");



    grp = fg
        .append("g")
        .attr("class", "v-sca")
        .attr("cursor", "pointer")
        .call(drag_listener_vs);
    grp
        .append("rect")
        .attr("fill", "darkslategrey")
        .attr("x", but_sca_v_x())
        .attr("y", but_sca_v_y())
        .attr("width", but_sca_long())
        .attr("height", but_sca_thick());

    grp
        .append("path")
        .attr("d", but_sca_tri_v(0))
        .attr("stroke", "white")
        .attr("fill", "white");


}


function def_drag_sca() {
    drag_listener_hs = d3.drag()
        .on("start", function(c) {
            if (fetch.done) {
                drag.sel = d3.select(this);
                drag.x = 0;
                drag.y = 0;
                drag.svg = d3.select("svg");
                drag.svg_w = +drag.svg.attr("width");
                drag.init = +drag.sel.select("rect").attr("x");
                dg.node().appendChild(drag.sel.node());


                drag.sel
                    .append("g")
                    .attr("class", "h-sca-l")
                    .append("line")
                    .attr("x1", drag.init)
                    .attr("y1", 0)
                    .attr("x2", drag.init)
                    .attr("y2", grid_height())
                    .attr("stroke", "black")
                    .attr("stroke-width", 2)
                    .attr("stroke-dasharray", "21,3,3,3");

            }
        })
        .on("drag", function(c) {
            if (fetch.done) {
                drag.x += d3.event.dx;
                if (drag.x + drag.init > 0) {
                    drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
                    if (drag.init + drag.x + margin.left + margin.right > drag.svg_w) {
                        drag.svg.attr("width", drag.init + drag.x + margin.left + margin.right);
                    }
                }
            }
        })
        .on("end", function(c) {
            if (fetch.done) {
                if (drag.x + drag.init <= 0) {
                    drag.x = -drag.init;
                }
                drag.sel.attr("transform", "translate(0,0)");
                drag.sel.select("rect").attr("x", drag.init + drag.x);
                if (rootgp_width != 0) {
                    labgp.width = ((drag.x + drag.init) / nbPer - dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) / rootgp_width;
                }
                drag.sel.select("path").attr("d", but_sca_tri_h(0));
                //(drag.x+drag.init)/(grid_width());
                go_edt(false);
                fg.node().appendChild(drag.sel.node());
                drag.sel.select(".h-sca-l").remove();
            }
        });

    drag_listener_vs = d3.drag()
        .on("start", function(c) {
            if (fetch.done) {
                drag.sel = d3.select(this);
                drag.x = 0;
                drag.y = 0;
                drag.init = +drag.sel.select("rect").attr("y");
                dg.node().appendChild(drag.sel.node());
                drag.svg = d3.select("svg")
                drag.svg_h = +drag.svg.attr("height"); //+200;

                drag.sel
                    .append("g")
                    .attr("class", "v-sca-l")
                    .append("line")
                    .attr("x1", 0)
                    .attr("y1", drag.init)
                    .attr("x2", but_sca_h_mid_x())
                    .attr("y2", drag.init)
                    .attr("stroke", "black")
                    .attr("stroke-width", 2)
                    .attr("stroke-dasharray", "21,3,3,3");

            }
        })
        .on("drag", function(c) {
            if (fetch.done) {
                drag.y += d3.event.dy;
                if (drag.init + drag.y >= 0) {
                    drag.sel.attr("transform",
				  "translate(" + drag.x + "," + drag.y + ")");
                    drag.svg.attr("height", drag.svg_h + drag.y);
                }
//                console.log(drag.svg.attr("height"));
            }
        })
        .on("end", function(c) {
            if (fetch.done) {
                if (drag.init + drag.y < 0) {
                    drag.y = -(drag.init);
                }
                labgp.height = labgp_from_grid_height(drag.init + drag.y) ;
		//                drag.sel.select("path").attr("d", but_sca_tri_v(drag.y));
                drag.sel.attr("transform", "translate(0,0)");
                drag.sel.select("rect").attr("y", grid_height());
		drag.sel.select("path").attr("d", but_sca_tri_v(0));
                go_edt(false);
                fg.node().appendChild(drag.sel.node());
                drag.sel.select(".v-sca-l").remove();

		svg.height = svg_height() ;
		d3.select("svg").attr("height", svg.height);

//		drag.svg.attr("height", svg_height());
            }
        });

}



/*----------------------
  ------- GROUPS -------
  ----------------------*/

// Only for the current case
function set_butgp() {
    var topx = 620;

    root_gp[0].buty = margin.but;
    root_gp[0].butx = topx;
    root_gp[1].buty = root_gp[0].buty + 3 * butgp.height + margin_but.ver;
    root_gp[1].butx = topx - .5 * margin_but.hor;
    root_gp[2].buty = root_gp[1].buty;
    root_gp[2].butx = root_gp[1].butx + margin_but.hor;


}



function indexOf_promo(promo) {
    for (var p = 0 ; p < set_promos.length ; p++ ) {
	if (set_promos[p] == promo_init ) {
	    return p ;
	}
    }
    return -1 ;
}

function go_promo_gp_init(button_available) {
    var gp_2_click = [] ;
    var found_gp, gpk, gpc, gpa ;

    if (promo_init != 0){
	promo_init = indexOf_promo(promo_init) ;
	if (gp_init == "") {
	    gp_init = root_gp[promo_init].gp.nom ;
	}
	if (Object.keys(groups[promo_init]).map(function(g) { return groups[promo_init][g].nom ; }).indexOf(gp_init) != -1) {
	    apply_gp_display(groups[promo_init][gp_init], true, button_available);
	}
    } else if (gp_init != "") {
	if (Object.keys(groups[0]).map(function(g) { return groups[0][g].nom ; }).indexOf(gp_init) != -1) {
	    apply_gp_display(groups[0][gp_init], true, button_available);
	}
    }
}


function create_groups(data_groups) {
    extract_all_groups_structure(data_groups);
    set_butgp();
    update_all_groups();
}


function extract_all_groups_structure(r) {
    var init_nbPromos = r.length;
    for (var npro = 0; npro < init_nbPromos; npro++) {
        extract_groups_structure(r[npro], -1, -1);
    }
}

function extract_groups_structure(r, npro, nrow) {
    var gr = {
        nom: r.name,
        ancetres: null,
        descendants: null,
        display: true,
        parent: null,
        children: null,
        x: 0,
        maxx: 0,
        width: 0,
        est: 0,
        lft: 0,
    }

    if ("undefined" === typeof r.buth) {
        gr.buth = 1;
    } else {
        gr.buth = r.buth * .01;
    }

    if (r.parent == "null") {

        // promo number should be unique
        set_promos.push(r.promo);

        npro = set_promos.indexOf(r.promo);


        // promo number should be unique
        groups[npro] = [];
        root_gp[npro] = {};


        root_gp[npro].gp = gr;

        if (set_rows.indexOf(r.row) == -1) {
            set_rows.push(r.row);
            row_gp[set_rows.indexOf(r.row)] = {};
            row_gp[set_rows.indexOf(r.row)].promos = [];
        }
        nrow = set_rows.indexOf(r.row);

        root_gp[npro].row = nrow;

        row_gp[nrow].promos.push(npro);

    } else {
        gr.parent = r.parent;
    }

    gr.promo = npro;


    if ("undefined" === typeof r.children || r.children.length == 0) {
        gr.children = [];
    } else {
        gr.children = r.children.map(function(d) {
            return d.name;
        });
        for (var i = 0; i < r.children.length; i++) {
            extract_groups_structure(r.children[i], npro, nrow);
        }
    }
    groups[npro][gr.nom] = gr;
}



// Earliest Starting Time (i.e. leftest possible position)
// for a node and its descendance, given node.est
function compute_promo_est_n_wh(node) {
    var child;


    if (node.parent == null) {
        node.ancetres = [];
        node.by = 0;
	root_gp[node.promo].maxby = node.by + node.buth ;
    } else {
	if (node.by + node.buth > root_gp[node.promo].maxby) {
	    root_gp[node.promo].maxby = node.by + node.buth ;
	}
    }
    node.descendants = [];


    node.width = 0;
    if (node.children.length == 0) {
        node.width = 1;
    } else {
        for (var i = 0; i < node.children.length; i++) {
            child = groups[node.promo][node.children[i]];
            child.est = node.est + node.width;
            child.by = node.by + node.buth;
            if (!child.display) {
                child.width = 0;
            } else {
                child.ancetres = node.ancetres.slice(0);
                child.ancetres.push(node.nom);
                compute_promo_est_n_wh(child);
                node.descendants = node.descendants.concat(child.descendants);
                node.descendants.push(child.nom);
            }
            node.width += child.width;
        }
    }
}

// Latest Finishing Time (i.e. rightest possible position)
// for a node and its descendance, given node.lft
function compute_promo_lft(node) {
    var child;
    var eaten = 0;
    for (var i = node.children.length - 1; i >= 0; i--) {
        child = groups[node.promo][node.children[i]];
        child.lft = node.lft - eaten;
        compute_promo_lft(child);
        eaten += child.width;
    }
}


// Least Mobile X 
function compute_promo_lmx(node) {
    var child;

    //    console.log(node.promo,node.nom,node.x,node.maxx);

    if (node.x < node.est) {
        node.x = node.est;
    }
    if (node.x + node.width > node.lft) {
        node.x = node.lft - node.width;
    }

    if (node.children.length == 0) {
        node.maxx = node.x + node.width;
    } else {
        var lastmax = node.x;
        var lastmin = -1;
        for (var i = 0; i < node.children.length; i++) {
            child = groups[node.promo][node.children[i]];
            if (child.display) {
                if (child.x < lastmax) {
                    child.x = lastmax;
                }
                compute_promo_lmx(child);
                if (lastmin == -1) {
                    lastmin = child.x;
                }
                lastmax = child.maxx;
            }
        }
        if (node.display) {
            node.maxx = lastmax;
            node.x = lastmin;
        }
    }

    //  //console.log(node.promo,node.nom,node.x,node.maxx);

}



function update_all_groups() {
    var max_rw = 0;
    var cur_rw, root, disp;

    // compute EST and width, and compute display row
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = 0;
        disp = false;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]].gp;
            root.est = cur_rw;
            compute_promo_est_n_wh(root);
            cur_rw += root.width;
            if (root.display) {
                row_gp[r].display = true;
            }
        }
        if (cur_rw > max_rw) {
            max_rw = cur_rw;
        }
    }
    rootgp_width = max_rw;

    if (rootgp_width > 0) {
        if (pos_rootgp_width == 0) {
            pos_rootgp_width = rootgp_width;
        }
        labgp.width *= pos_rootgp_width / rootgp_width;
        pos_rootgp_width = rootgp_width;
    }



    // compute LFT
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = max_rw;
        for (var p = row_gp[r].promos.length - 1; p >= 0; p--) {
            root = root_gp[row_gp[r].promos[p]].gp;
            root.lft = cur_rw;
            compute_promo_lft(root);
            cur_rw -= root.width;
        }
    }
    // move x if necessary
    for (var r = 0; r < set_rows.length; r++) {
        cur_rw = 0;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root = root_gp[row_gp[r].promos[p]].gp;
            if (root.x < cur_rw) {
                root.x = cur_rw;
            }
            compute_promo_lmx(root);
            cur_rw = root.maxx;
        }
    }

    // move y if necessary
    nbRows = 0;
    for (var r = 0; r < set_rows.length; r++) {
        root = row_gp[r];
        root.display = false;
        root.y = nbRows;
        for (var p = 0; p < row_gp[r].promos.length; p++) {
            root.display = root.display || root_gp[root.promos[p]].gp.display;
        }
        if (root.display) {
            nbRows += 1;
        }
    }

    if (nbRows > 0) {
        if (pos_nbRows == 0) {
            pos_nbRows = nbRows;
        }
        labgp.height *= pos_nbRows / nbRows;
        pos_nbRows = nbRows;
    }


    //    compute_promo_lmx(node)
}



// data related to leaves
function compute_promo_leaves(node) {
    var gp;

    if (node.children.length == 0) {
        for (var j = 0; j < nbPer; j++) {
            data_grid_scale_gp.push({
                day: j,
                gp: node
            });
            for (var s = 0; s < nbSl; s++) {
                if (!is_free(j, s, node.promo)) {
                    data_mini_slot_grid.push({
                        day: j,
                        slot: s,
                        gp: node
                    });
                }
            }
        }
    }

    for (var i = 0; i < node.children.length; i++) {
        child = groups[node.promo][node.children[i]];
        compute_promo_leaves(child);
    }
}


/*--------------------
  ------ MENUS -------
  --------------------*/



function create_menus() {

    meg
        .attr("transform", "translate(" + menus.x + "," + menus.y + ")")
        .attr("text-anchor", "start")
        .attr("font-size", 18);

    meg
        .append("rect")
        .attr("class", "menu")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
        .attr("rx", 10)
        .attr("ry", 10);

    meg
        .append("rect")
        .attr("class", "menu")
        .attr("x", menus.dx)
        .attr("y", 0)
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
        .attr("rx", 10)
        .attr("ry", 10);

    meg
        .append("text")
        .attr("x", menus.mx)
        .attr("y", menus.h - 10)
        .attr("fill", "black")
        .text("Cours :");

    meg
        .append("text")
        .attr("x", menus.mx + menus.dx)
        .attr("y", menus.h - 10)
        .attr("fill", "black")
        .text("Dispos :");

    go_menus();
}



/*---------------------
  ------- BKNEWS -----
  ---------------------*/

function translate_bknews_from_csv(d){
    return {
	x_beg: +d.x_beg,
	x_end: +d.x_end,
	y: +d.y,
	fill_col: d.fill_col,
	strk_col: d.strk_col,
	txt: d.txt
    }
}



/*--------------------
   ------ COURS ------
  --------------------*/


function assign_fill_mod() {
    for (var c = 0; c < cours.length; c++) {
        var s = cours[c].mod;
        if (Object.keys(mod2col).indexOf(s) == -1) {
            var hash = 0,
                i, chr;
            if (s.length === 0) {
                hash = 0;
            }
            for (i = 0; i < s.length; i++) {
                chr = s.charCodeAt(i);
                hash = ((hash << 2) - hash) + chr;
                hash |= 0; // Convert to 32bit integer
            }
            hash = hash % couleurs_fond_texte.length;
            mod2col[s] = couleurs_fond_texte[hash];
        }
    }
}


function def_drag() {
    var cur_over = null;
    var sl = null;
    dragListener = d3.drag()
        .on("start", function(c) {
            if (ckbox["edt-mod"].cked && fetch.done) {

                data_slot_grid.forEach(function(sl) {
                    check_cours(c, sl);
                });

                drag.x = 0;
                drag.y = 0;

                drag.sel = d3.select(this);
                dg.node().appendChild(drag.sel.node());


            }
        })
        .on("drag", function(d) {
            if (ckbox["edt-mod"].cked && fetch.done) {
                cur_over = which_slot(drag.x +
				      parseInt(drag.sel.select("rect")
					       .attr("x")),
				      drag.y +
				      parseInt(drag.sel.select("rect")
					       .attr("y")),
				      cours_width(d),
				      cours_height(d));

                if (!is_garbage(cur_over.day,cur_over.slot)) {
                    sl = data_slot_grid.filter(function(c) {
                        return c.day == cur_over.day && c.slot == cur_over.slot;
                    });
                    if (sl != null && sl.length > 0) {
                        if (!sl[0].display) {
                            data_slot_grid.forEach(function(s) {
                                s.display = false;
                            });
                            sl[0].display = true;
                        }
                    }
                } else {
                    data_slot_grid.forEach(function(s) {
                        s.display = false;
                    });
                }
                go_grid(true);

                drag.x += d3.event.dx;
                drag.y += d3.event.dy;
                drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
            }
        }).on("end", function(d) {
            if (ckbox["edt-mod"].cked && fetch.done) {

                mg.node().appendChild(drag.sel.node());

                data_slot_grid.forEach(function(s) {
                    s.display = false;
                });


                if (!is_garbage(cur_over.day,cur_over.slot)) {
                    var ngs = data_slot_grid.filter(function(s) {
                        return s.day == cur_over.day && s.slot == cur_over.slot;
                    })[0];


                    if (ngs.dispo) {
                        add_bouge(d);
                        ////console.log(cours_bouge);
                        d.day = cur_over.day;
                        d.slot = cur_over.slot;
                    } else {
                        ngs.pop = true;
                    }
                } else {
                    d.day = cur_over.day;
                    d.slot = cur_over.slot;
		}

                drag.sel.attr("transform", "translate(0,0)");

                drag.x = 0;
                drag.y = 0;
                drag.sel = null;
                cur_over = null;

                go_grid(true);
                go_cours(true);
            }
        });

}

function check_cours(c2m, grid_slot) {


    grid_slot.dispo = true;
    grid_slot.reason = "";


    if (is_garbage(grid_slot.day, grid_slot.slot)) {
	return ;
    }

    if (c2m.id_cours == -1) {
	grid_slot.dispo = false;
	grid_slot.reason = "Cours fixe";
	return ;
    }

    if (is_free(grid_slot.day, grid_slot.slot, c2m.promo)) {
        grid_slot.dispo = false;
        grid_slot.reason = "CRENEAU NON DISPO POUR " + set_promos[c2m.promo] + "A";
        return;
    }


    var cs = cours.filter(function(c) {
        return (c.day == grid_slot.day &&
            c.slot == grid_slot.slot &&
            c.prof == c2m.prof);
    });
    if (cs.length > 0 && cs[0] != c2m) {
        grid_slot.dispo = false;
        grid_slot.reason = "PB PROF OCCUPE";
        return;
    }


    cs = cours.filter(function(c) {
        return (c.day == grid_slot.day &&
            c.slot == grid_slot.slot &&
            (c.group == c2m.group ||
                groups[c2m.promo][c2m.group].ancetres.indexOf(c.group) > -1 ||
                groups[c2m.promo][c2m.group].descendants.indexOf(c.group) > -1) &&
            c.promo == c2m.promo);
    });
    if (cs.length > 0 && cs[0] != c2m) {
        grid_slot.dispo = false;
        grid_slot.reason = "PB GROUPE";
        return;
    }

    if (dispos[c2m.prof] !== undefined &&
        dispos[c2m.prof][grid_slot.day][grid_slot.slot] == 0) {
        grid_slot.dispo = false;
        grid_slot.reason = "PB PROF PAS DISPO";
        return;
    }


}

function which_slot(x, y, w, h) {
    var wday = (rootgp_width * labgp.width +
        dim_dispo.plot *
        (dim_dispo.width + dim_dispo.right));
    var day = Math.floor((x + .5 * w) / wday);
    // if (day < 0 || day >= nbPer ||
    //     (x + .5 * w - day * wday > rootgp_width * labgp.width)) {
    //     return null;
    // }
    var hslot = nbRows * labgp.height;
    var slot = Math.floor((y + .5 * h) / hslot);
    // if ((slot < 0 || slot >= nbSl) && !is_garbage(day, slot)) {
    //     return null;
    // }
    return {
        day: day,
        slot: slot
    };
}


function is_garbage(day, hour) {
    return (hour >= nbSl || hour < 0 || day < 0 || day >= nbPer);
}

function is_free(day, hour, promo) {
    return (promo < 2 && (day == 3 && hour > 2));
}



/*---------------------
  ------- VALIDER -----
  ---------------------*/

function create_forall_prof() {
    var contg = prg
        .append("g")
        .attr("class", "profs-but-fa")
        .attr("transform", "translate(" + butpr.tlx + "," + butpr.tly + ")")
        .attr("cursor", "pointer")
        .on("click", apply_pr_all);


    contg
        .append("rect")
        .attr("width", butpr.width)
        .attr("height", butpr.height)
        .attr("class", "profs-but-me")
        .attr("rx", 5)
        .attr("ry", 10)
        .attr("x", 0)
        .attr("y", 0);

    contg
        .append("text")
        .text("\u2200")
        .attr("x", .5 * butpr.width)
        .attr("y", .5 * butpr.height);
}



/*---------------------
  ------- VALIDER -----
  ---------------------*/

function create_val_but() {

    edt_but = vg
        .append("g")
        .attr("but", "edt")
        .on("mouseover", but_bold)
        .on("mouseout", but_back)
        .on("click", confirm_change)
        .attr("cursor", "pointer");

    edt_but
        .append("rect")
        .attr("width", valid.w)
        .attr("height", valid.h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly); //menus.y+menus.h);

    edt_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .text("Valider EdT")
        .attr("x", menus.x + menus.mx + .5 * valid.w)
        .attr("y", did.tly + .5 * valid.h);

    edt_but.attr("visibility", "hidden");


    edt_message = vg
        .append("g")
        .attr("message", "edt");

    edt_message
        .append("rect")
        .attr("width", menus.coled + menus.colcb)
        .attr("height", 30)
        .attr("fill", "white")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", menus.x)
        .attr("y", did.tly + 94);

    edt_message
        .append("g")
        .attr("class", "ack-edt")
        .append("text")
        .attr("x", menus.x + (menus.coled + menus.colcb) * 0.5)
        .attr("y", did.tly + 94 + 15);

    edt_message.attr("visibility", "hidden");

    vg
        .append("g")
        .attr("class", "ack-reg")
        .append("text");


}




/*--------------------
   ------ STYPE ------
  --------------------*/

function create_stype() {
    var t, dat, datdi, datsmi;

    // sometimes, all dispos are not in the database
    // -> by default, not available
    for (var i = 0; i < user.dispos_type.length; i++) {
        if (typeof user.dispos_type[i] == 'undefined') {
            // cf translate_dispos_type_from_csv
            user.dispos_type[i] = create_dispo_default_from_index(i);
        }
    }


    dat = stg.selectAll(".dispot")
        .data(user.dispos_type);

    datdi = dat
        .enter()
        .append("g")
        .attr("class", "dispot")
        .attr("transform", "translate(" +
            did.tlx + "," +
            did.tly + ")");

    var datdisi = datdi
        .append("g")
        .attr("class", "dispot-si");



    datdisi
        .append("rect")
        .attr("class", "dispot-bg")
        .attr("stroke", "#555555")
        .attr("stroke-width", 1)
        .attr("fill", function(d) {
            return smi_fill(d.val / par_dispos.nmax);
        })
        .attr("width", dispot_w)
        .attr("height", dispot_h)
        .attr("x", dispot_x)
        .attr("y", dispot_y)
        .attr("fill", function(d) {
            return smi_fill(d.val / par_dispos.nmax);
        });

    datdisi
        .append("line")
        .attr("stroke", "#555555")
        .attr("stroke-width", 2)
        .attr("x1", 0)
        .attr("y1", gsclbt_y)
        .attr("x2", gsclbt_x)
        .attr("y2", gsclbt_y);

    stg.attr("visibility", "hidden");

    var dis_but = stg
        .append("g")
        .attr("but", "dis")
        .on("mouseover", but_bold)
        .on("mouseout", but_back)
        .on("click", send_dis_change)
        .attr("cursor", "pointer");

    dis_but
        .append("rect")
        .attr("width", valid.w)
        .attr("height", valid.h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", did.tlx)
        .attr("y", did.tly);

    dis_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .text("Valider disponibilités")
        .attr("x", did.tlx + .5 * valid.w)
        .attr("y", did.tly + .5 * valid.h);

    var stap_but = stg
        .append("g")
        .attr("but", "st-ap")
        .on("mouseover", st_but_bold)
        .on("mouseout", st_but_back)
        .on("click", apply_stype)
        .attr("cursor", st_but_ptr);

    stap_but
        .append("rect")
        .attr("width", stbut.w)
        .attr("height", stbut.h + 20)
        .attr("x", dispot_but_x)
        .attr("y", dispot_but_y("app"))
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2);

    stap_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .attr("x", dispot_but_txt_x)
        .attr("y", dispot_but_txt_y("app"))
        .text("Appliquer");

    stap_but
        .append("text")
        .attr("font-size", 18)
        .attr("fill", "white")
        .attr("x", dispot_but_txt_x)
        .attr("y", dispot_but_txt_y("app") + 20)
        .text("Semaine type");

}



function fetch_dispos_type() {
    if (user.nom != "") {
        show_loader(true);
        $.ajax({
            type: "GET", //rest Type
            dataType: 'text',
            url: url_fetch_stype,
            async: true,
            contentType: "text/csv",
            success: function(msg) {
                //console.log(msg);

                //console.log("in");
                user.dispos_type = new Array(nbSl * nbPer); // - nbSl/2);

                d3.csvParse(msg, translate_dispos_type_from_csv);
                create_stype();
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
}


function translate_dispos_type_from_csv(d) {
    var d2p = {
        day: +d.jour,
        hour: +d.heure,
        val: +d.valeur,
        off: -1
    };
    //    if(!is_free(+d.jour,+d.heure)){
    user.dispos_type[day_hour_2_1D(d2p)] = d2p;
    //    }
}

function create_dispo_default_from_index(ind) {
    return {
        day: Math.floor(ind / nbSl),
        hour: ind % nbSl,
        val: 0,
        off: -1
    };
    //d.day<4?d.day*nbSl+d.hour:d.day*nbSl+d.hour-3;
}






/*--------------------
   ------ ALL -------
  --------------------*/



function on_group_rcv(dg) {

    create_groups(dg);


    /*
    if (promo_init != 1 && promo_init != 2) {
        go_gp_buttons();
    }
    */
    go_gp_buttons();

//    var expected_ext_grid_dim = svg.height - margin.top - margin.bot
    //	- valid.margin_edt - 3.5 * valid.h;




    create_edt_grid();
//    go_grid(false);

    create_alarm_dispos();
    create_val_but();
    go_val_but();

    create_bknews();

    go_promo_gp_init() ;
    go_gp_buttons();


//    d3.select("svg").attr("height", svg_height());

    //console.log(d3.select("svg").attr("height"));
    //console.log(margin.top + ack_reg_y() + 4*margin.bot);

    fetch_cours();
    fetch_bknews(true);

    if (splash_id == 1) {
    
	var splash_mail = {
	    id: "mail-sent",
	    but: {list: [{txt: "Ok", click: function(d){} }]},
	    com: {list: [{txt: "E-mail envoyé !", ftsi: 23}]}
	}
	splash(splash_mail);

    } else if (splash_id == 2) {

	var splash_quote = {
	    id: "quote-sent",
	    but: {list: [{txt: "Ok", click: function(d){} }]},
	    com: {list: [{txt: "Citation envoyée ! (en attente de modération)", ftsi: 23}]}
	}
	splash(splash_quote);

    }
    
    //go_edt(true);
}






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
    fetch.done = false;
    fetch.dispos_ok = true;

    var semaine_att = weeks.init_data[weeks.sel[0]].semaine;
    var an_att = weeks.init_data[weeks.sel[0]].an;
    
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_dispos + "?s=" + semaine_att + "&a=" + an_att,
        async: true,
        contentType: "text/csv",
        success: function(msg) {
            console.log("in");
            //console.log(msg);
            prev_prof = "";

            if (semaine_att == weeks.init_data[weeks.sel[0]].semaine &&
                an_att == weeks.init_data[weeks.sel[0]].an) {
                dispos = [];
                //user.dispos = [];
                d3.csvParse(msg, translate_dispos_from_csv);

                fetch.ongoing_dispos = false;
                if (ckbox["dis-mod"].cked) {
                    create_dispos_user_data();
                }

                fetch_ended();
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
            window.location.replace(url_login + "?next=" + url_edt + an_att + "/" + semaine_att);
        }
    });
}


function translate_dispos_from_csv(d) {
    if (d.prof != prev_prof) {
        prev_prof = d.prof;
        dispos[d.prof] = new Array(nbPer);
        for (var i = 0; i < nbPer; i++) {
            dispos[d.prof][i] = new Array(nbSl);
            dispos[d.prof][i].fill(-1);
        }
    }
    dispos[d.prof][+d.jour][+d.heure] = +d.valeur;
}



// off: offset useful for the view. Quite unclean.
function create_dispos_user_data() {

    var d, j, k, d2p;

    user.dispos = [];
    user.dispos_bu = [];

    var current;

    if (dispos[user.nom] === undefined) {
        dispos[user.nom] = new Array(nbPer);
        for (var i = 0; i < nbPer; i++) {
            dispos[user.nom][i] = new Array(nbSl);
            dispos[user.nom][i].fill(-1);
        }
    }


    for (var j = 0; j < nbPer; j++) {
        for (var k = 0; k < nbSl; k++) {
            //	    if(!is_free(j,k)) {
            d2p = {
                day: j,
                hour: k,
                val: dispos[user.nom][j][k],
                off: -1
            };
            user.dispos_bu.push(d2p);
            if (dispos[user.nom][j][k] < 0) {
                dispos[user.nom][j][k] = user.dispos_type[day_hour_2_1D(d2p)].val; //par_dispos.nmax;
                //console.log(j,k,day_hour_2_1D(d2p),user.dispos_type[day_hour_2_1D(d2p)])
            }
            user.dispos.push({
                day: j,
                hour: k,
                val: dispos[user.nom][j][k],
                off: -1
            });

            //	    }
        }
    }

}



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

function create_mod_dd() {


    var seldd = mog
        .selectAll("option")
        .data(modules.all, function(d, i) {
            return d;
        });

    seldd
        .enter()
        .append("option")
        .merge(seldd.select("option"))
        .attr("value", function(d) {
            return d;
        })
        .text(function(d) {
            return d;
        });

    seldd.exit().remove();

    seldd
        .each(function(d, i) {
            if (d == modules.sel) {
                d3.select(this).attr("selected", "");
            }
        });


}


/*----------------------
  ------ SALLES -------
  ----------------------*/

function create_sal_dd() {


    var seldd = sag
        .selectAll("option")
        .data(salles.all, function(d, i) {
            return d;
        });

    seldd
        .enter()
        .append("option")
        .merge(seldd.select("option"))
        .attr("value", function(d) {
            return d;
        })
        .text(function(d) {
            return d;
        });

    seldd.exit().remove();

    seldd
        .each(function(d, i) {
            if (d == salles.sel) {
                d3.select(this).attr("selected", "");
            }
        });


}


/*--------------------
  ------ PROFS -------
  --------------------*/
function create_pr_buttons() {
    var t = d3.transition();
    profs.sort();

    var cont =
        prg.selectAll(".profs-but")
        .data(profs, function(p) {
            return p;
        });

    var contg = cont
        .enter()
        .append("g")
        .attr("class", "profs-but")
        .attr("transform", "translate(" + butpr.tlx + "," + butpr.tly + ")")
        .on("click", apply_pr_display);

    contg
        .append("rect")
        .attr("class", butpr_class)
        .attr("width", butpr.width)
        .attr("height", butpr.height)
        .attr("rx", 5)
        .attr("ry", 10)
        .merge(cont.select("rect"))
        .attr("x", butpr_x)
        .attr("y", butpr_y);

    contg
        .append("text")
        .attr("class", butpr_class)
        .text(function(d) {
            return d;
        })
        .merge(cont.select("text"))
        .attr("x", butpr_txt_x)
        .attr("y", butpr_txt_y);

    cont.exit().remove();
}



/*--------------------
  ------ BKNEWS -------
  --------------------*/
function fetch_bknews(first) {
    fetch.ongoing_bknews = true;
    var semaine_att = weeks.init_data[weeks.sel[0]].semaine;
    var an_att = weeks.init_data[weeks.sel[0]].an;

    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_bknews + "?w=" + semaine_att + "&y=" + an_att,
        async: true,
        contentType: "text/json",
        success: function(msg) {
            //console.log(msg);

            bknews.cont = JSON.parse(msg) ;

            if (semaine_att == weeks.init_data[weeks.sel[0]].semaine &&
                an_att == weeks.init_data[weeks.sel[0]].an) {
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

		}

		
		
                fetch.ongoing_bknews = false;
                fetch_ended();
            }
            show_loader(false);
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });


}

function adapt_labgp(first) {
    var expected_ext_grid_dim = svg.height - margin.top - margin.bot ;
    var new_gp_dim;

    if (nbRows > 0) {
        new_gp_dim = expected_ext_grid_dim / (nb_vert_labgp_in_grid() + nbRows) ;
        if (new_gp_dim > labgp.hm) {
            labgp.height = new_gp_dim;
        } else {
            labgp.height = labgp.hm;
        }
    } // sinon ?
    svg.height = svg_height() ;
    d3.select("svg").attr("height", svg.height);


    if (first) {
	expected_ext_grid_dim = svg.width - margin.left - margin.right;
	new_gp_dim = expected_ext_grid_dim / (rootgp_width * nbPer);
	if (new_gp_dim > labgp.wm) {
            labgp.width = new_gp_dim;
	} else {
            labgp.width = labgp.wm;
	}
	d3.select("svg").attr("width", svg.width);
    }

}


/*--------------------
  ------ COURS -------
  --------------------*/

function fetch_cours() {
    var garbage_plot ;
    
    fetch.ongoing_cours_pp = true;
    fetch.ongoing_cours_pl = true;
    fetch.cours_ok = false;

    fetch.done = false;
    ack.edt = "";
    go_val_but(true);

    var semaine_att = weeks.init_data[weeks.sel[0]].semaine;
    var an_att = weeks.init_data[weeks.sel[0]].an;

    cours_bouge = {};
    
    show_loader(true);
    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_cours_pl + "?s=" + semaine_att + "&a=" + an_att + "&c=" + num_copie,
        async: true,
        contentType: "text/csv",
        success: function(msg, ts, req) {
            //console.log(msg);
            version = +req.getResponseHeader('version');
            required_dispos = +req.getResponseHeader('reqDispos');
            filled_dispos = +req.getResponseHeader('filDispos');

            go_regen(req.getResponseHeader('regen'));
            go_alarm_dispos();

            var day_arr = JSON.parse(req.getResponseHeader('jours').replace(/\'/g, '"'));
            for (var i = 0; i < day_arr.length; i++) {
                data_grid_scale_day[i] = data_grid_scale_day_init[i] + " " + day_arr[i];
            }
            //console.log(data_grid_scale_day);
            if (semaine_att == weeks.init_data[weeks.sel[0]].semaine &&
                an_att == weeks.init_data[weeks.sel[0]].an) {

                profs_pl = [];
                modules.pl = [];
                salles.pl = [];

                cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);


                fetch.ongoing_cours_pl = false;
                fetch_ended();
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
        url: url_cours_pp + "?s=" + semaine_att + "&a=" + an_att + "&c=" + num_copie,
        async: true,
        contentType: "text/csv",
        success: function(msg, ts, req) {
            //console.log(msg);

            if (semaine_att == weeks.init_data[weeks.sel[0]].semaine &&
                an_att == weeks.init_data[weeks.sel[0]].an) {

                profs_pp = [];
                modules.pp = [];
                salles.pp = [];

                //console.log(msg);
		console.log(semaine_att,an_att,num_copie);

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

                //console.log(msg);

                fetch.ongoing_cours_pp = false;
                fetch_ended();
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
    var ind = profs_pl.indexOf(d.prof_nom);
    if (ind == -1) {
        profs_pl.push(d.prof_nom);
    }
    if (modules.pl.indexOf(d.module) == -1) {
        modules.pl.push(d.module);
    }
    if (salles.pl.indexOf(d.room) == -1) {
        salles.pl.push(d.room);
    }
    var co = {
        id_cours: +d.id_cours,
        no_cours: +d.num_cours,
        prof: d.prof_nom,
        prof_full_name: d.prof_first_name + " " + d.prof_last_name,
        group: translate_gp_name(d.gpe_nom),
        promo: set_promos.indexOf(+d.gpe_promo),
        mod: d.module,
        day: +d.jour,
        slot: +d.heure,
        room: d.room
    };
    //    console.log(co);
    return co;
}


function translate_cours_pp_from_csv(d) {
    if (profs_pp.indexOf(d.prof) == -1) {
        profs_pp.push(d.prof);
    }
    if (modules.pp.indexOf(d.module) == -1) {
        modules.pp.push(d.module);
    }
    if (salles.pp.indexOf(d.room) == -1) {
        salles.pp.push(d.room);
    }
    var co = {
        id_cours: +d.id,
        no_cours: +d.no,
        prof: d.prof,
        group: translate_gp_name(d.groupe),
        promo: set_promos.indexOf(+d.promo),
        mod: d.module,
        day: garbage.day,
        slot: garbage.slot,
        room: une_salle
    };
    console.log(co);
    return co;
}



// Add pseudo-courses that do not appear in the database //
function add_exception_course(cur_week, cur_year, targ_week, targ_year,
			      day, slot, group, promo, l1, l2, l3) {
    if (cur_week == targ_week && cur_year == targ_year) {
	cours.push({day: day,
		    slot: slot,
		    group: group,
		    promo: set_promos.indexOf(promo),
		    id_cours: -1,
		    no_cours: -1,
		    mod: l1,
		    prof: l2,
		    room: l3
		   });
    }
}



// Pseudo fonction pour des possibles exceptions //
/*
"Passeport Avenir (Bénéficiaires d'une bourse)"
"--- 13h30 ---"
"Amphi 1"
"exception"
function add_exception(sem_att, an_att, sem_voulue, an_voulu, nom, l1, l2, l3){
    if(sem_att==sem_voulue && an_att==an_voulu){
	var gro = dg.append("g")
	    .attr("class",nom);

	var tlx = 3*(rootgp_width*labgp.width
		     + dim_dispo.plot*(dim_dispo.width+dim_dispo.right))
	    + groups[0]["P"].x*labgp.width ;
	var tlx2 = tlx + .5*groups[0]["P"].width*labgp.width;

	var tly = (3*nbPromos + row_gp[0].y)*(labgp.height) ;
	
	gro
	    .append("rect")
	    .attr("x", tlx  )
	    .attr("y", tly )
	    .attr("fill","red")
	    .attr("width",groups[0]["P"].width*labgp.width)
	    .attr("height",labgp.height);

	gro.append("text")
	    .text(l1)
	    .attr("font-weight","bold")
	    .attr("x",tlx2 )
	    .attr("y",tly + labgp.height/4);
	gro.append("text")
	    .text(l2)
	    .attr("font-weight","bold")
	    .attr("x",tlx2 )
	    .attr("y",tly + 2*labgp.height/4);
	gro.append("text")
	    .text(l3)
	    .attr("font-weight","bold")
	    .attr("x",tlx2 )
	    .attr("y",tly + 3*labgp.height/4);
	
    } else {
	d3.select("."+nom).remove();
    }
}
*/

function clean_prof_displayed() {

    var all = (profs.length == prof_displayed.length);

    profs = profs_pl;
    for (var i = 0; i < profs_pp.length; i++) {
        var ind = profs.indexOf(profs_pp[i]);
        if (ind == -1) {
            profs.push(profs_pp[i]);
        }
    }



    if (all) {
        prof_displayed = profs.slice(0);
    } else {

        var ndi = prof_displayed.filter(function(d) {
            return profs.indexOf(d) > -1;
        });

        if (ndi.length == 0) {
            prof_displayed = profs.slice(0);
        } else {
            prof_displayed = ndi;
        }

    }
}

function translate_gp_name(gp) {
    var ret = gp.slice(2);
    if (ret == "") {
        ret = "P";
    }
    return ret;
}


/*--------------------
   ------ ALL -------
  --------------------*/
function fetch_ended() {
    if (!fetch.ongoing_cours_pl &&
        !fetch.ongoing_cours_pp) {
        cours = cours_pl.concat(cours_pp);

        modules.all = [""].concat(modules.pl);
        for (var i = 0; i < modules.pp.length; i++) {
            if (modules.all.indexOf(modules.pp[i]) == -1) {
                modules.all.push(modules.pp[i]);
            }
        }

        modules.all.sort();

        if (modules.all.indexOf(modules.sel) == -1) {
            modules.sel = "";
        }


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

        create_mod_dd();
        create_sal_dd();
        clean_prof_displayed();
        assign_fill_mod();
        fetch.cours_ok = true;
    }

    if (!fetch.ongoing_cours_pp &&
        !fetch.ongoing_cours_pl &&
        !fetch.ongoing_dispos &&
        !fetch.ongoing_bknews) {

        fetch.done = true;
        go_edt(false);

	if (fig === undefined) {
            fig = svg_cont.append("g")
		.attr("id", "lay-final");
	}

    }
    //go_gp_buttons();
    create_pr_buttons();
    go_profs();



}
/*----------------------
   ------ LOADER -------
  ----------------------*/

var cpt_loader = 0;

// show/hide le div 'loader' and count method's call
// the loader is hide only if cpt_loader==0
function show_loader(doit) {
    if (doit) {
        cpt_loader ++;
        $('#loader').css("visibility", "visible");
    } else {
        cpt_loader --;
        if (cpt_loader<=0) {
            cpt_loader=0;
            $('#loader').css("visibility", "hidden");
        }
    }
    //console.log('loader : '+doit+' cpt='+cpt_loader);
}









/* 
Reste :
  x couleur modules
  x display filtre prof
  x semaines (fetch, go_course, go_dispo)
  x modif edt (d&d, struct edt, check, display conflits, semaine pro)
  o modif dispos (simple, 0-9, semaine type)
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
