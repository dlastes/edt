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
    var t = time_settings.time ;
    return nbRows * scale * (t.lunch_break_start_time - t.day_start_time);
}
function bknews_bot_y() {
    return bknews_top_y() +  bknews_h() ;
}
function bknews_h() {
    if (bknews.nb_rows == 0) {
	return 0;
    } else {
	return bknews.nb_rows * bknews_row_height()
	    + 2 * bknews.time_margin * scale ;
    }
}

function bknews_row_x(d){
    return (d.x_beg * (rootgp_width * labgp.width
		       + dim_dispo.plot * (dim_dispo.width + dim_dispo.right))) ;
}
function bknews_row_y(d){
    return bknews_top_y() + bknews.time_margin * scale
	+ d.y * bknews.time_height * scale ;
}
function bknews_row_fill(d){
    return d.fill_color ;
}
function bknews_row_width(d){
    return ((d.x_end - d.x_beg) * (rootgp_width * labgp.width
		       + dim_dispo.plot * (dim_dispo.width + dim_dispo.right))) ;
}
function bknews_row_height(d){
    return bknews.time_height * scale ;
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
function bknews_link(d){
    return d.is_linked ;
}


/*---------------------
  ------- ALL ------
  ---------------------*/

function svg_height() {
    //    return margin.top + ack_reg_y() + 4*margin.bot ;
    return margin.top + grid_height() + margin.bot
     + scale * garbage.duration * nbRows;
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
function dispo_x(d) {
    return idays[d.day].num * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        rootgp_width * labgp.width ;
}



// -- no slot --
// --  begin  --
// TO BE IMPROVED for multi-line, and lunch break
function dispo_y(d) {
    var t = time_settings.time ;
    var ret = (d.start_time-t.day_start_time) * nbRows * scale ;
//	+ row_gp[root_gp[c.promo].row].y * rev_constraints[c.start.toString()] * scale ;
    if (d.start_time >= t.lunch_break_finish_time) {
	ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time)*nbRows*scale ;
    }
    return ret ;
}
// --   end   --
// -- no slot --

function dispo_w(d) {
    return dim_dispo.plot * dim_dispo.width;
}

function dispo_h(d) {
    return nbRows * d.duration * scale ;
}

function dispo_fill(d) {
    return smi_fill(d.val / par_dispos.nmax);
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
    return .25 * dispo_h(d);
}

function dispo_more_y(d) {
    return dispo_y(d) + dispo_h(d) - dispo_more_h(d);
}

function dispo_more_x(d) {
    return dispo_x(d) + dispo_w(d) - dispo_more_h(d);
}

function dispo_all_x(d) {
    return dispo_more_x(d) + dispo_more_h(d)
       - par_dispos.adv_red * dispo_w(d);
}

function dispo_all_h(d) {
    return 2 * dim_dispo.adv_v_margin + 2 * smiley.tete;
}

function dispo_all_y(d) {
    var ts = time_settings.time ;
    if (d.start_time < ts.lunch_break_start_time) {
	return dispo_more_y(d) + d.off * dispo_all_h(d);
    } else {
	return dispo_more_y(d) - d.off * dispo_all_h(d);
    }
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
    // -- no slot --
    // --  begin  --
    // TO CHECK
    return d.off == -1 ? d.val / par_dispos.nmax : d.off / par_dispos.nmax;
    // --   end   --
    // -- no slot --
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
            (dispo_y(d) + .5 * dispo_h(d)) + ")";
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

function gs_x(d) {
    return idays[d.day].num * (rootgp_width * labgp.width +
        dim_dispo.plot * (dim_dispo.width + dim_dispo.right));
}

function gs_y(d) {
    var t = time_settings.time ;
    var ret = (d.start - t.day_start_time) * nbRows * scale ;
    if (d.start >= t.lunch_break_finish_time) {
	ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time)*nbRows*scale ;
    }
    return ret ;
}

function gs_width(d) {
    return rootgp_width * labgp.width;
}

function gs_height(d) {
    return d.duration * nbRows * scale ;
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
    return d.start < time_settings.time.day_finish_time ? "black" : "red";
}


function gscg_x(datum) {
    // hack for LP
    var hack = 0;
    if (datum.gp.nom == "fLP1") {
        hack = .5 * labgp.width;
    }
    return datum.day * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        datum.gp.x * labgp.width +
        .5 * labgp.width +
        hack;
}

function gscg_y(datum) {
    if (datum.gp.promo == 0 || set_rows.length == 1) {
        return -.25 * labgp.height_init;
    } else {
        // if (datum.day == 3) {
        //     return .5 * grid_height() + .25 * labgp.height_init;
        // }
        return grid_height() + .25 * labgp.height_init;
    }
}

function gscg_txt(datum) {
    if (datum.gp.nom == "fLP1") {
        return "LP";
    } else if (datum.gp.nom == "fLP2") {
        return "";
    } else {
        return datum.gp.nom;
    }
}

function gscp_x(datum) {
    return -.7 * labgp.width_init;
}

function gscp_y(d) {
    var t = time_settings.time ;
    var ret = (d.start-t.day_start_time) * nbRows * scale
	+ row_gp[d.row].y * rev_constraints[d.start.toString()] * scale ;
    if (d.start >= t.lunch_break_finish_time) {
	ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time)*nbRows*scale ;
    }
    return ret + .5*d.duration*scale;
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
    return d.name + " " + d.date;
}


function grid_day_am_x(d) {
    return d.num * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right));
}
function grid_day_am_y(d) {
    return 0 ;
}
function grid_day_am_height(d) {
    var t = time_settings.time ;
    return scale*nbRows*(t.lunch_break_start_time - t.day_start_time) ;
}
function grid_day_am_width(d) {
    return rootgp_width * labgp.width ;
}
function grid_day_pm_x(d) {
    return grid_day_am_x(d) ;
}
function grid_day_pm_y(d) {
    var t = time_settings.time ;
    return grid_day_am_y(d) + grid_day_am_height(d)
	+ bknews_h() ;
}
function grid_day_pm_height(d) {
    var t = time_settings.time ;
    return scale*nbRows*(t.day_finish_time - t.lunch_break_finish_time) ;
}
function grid_day_pm_width(d) {
    return rootgp_width * labgp.width ;
}


function gsckh_x(datum) {
    return grid_width() + 5 ;//.25 * labgp.width;
}

function gsckh_y(datum, i) {
    var ret = (i + .5) * dispo_h(datum);
    if (!pref_only && i >= bknews.hour_bound) {
	ret += bknews_h() ;
    }
    return ret ;
}

function gsckh_txt(d) {
    return d;
}

function grid_height() {
    return scale * nb_minutes_in_grid();
}

function nb_minutes_in_grid() {
    var t = time_settings.time ;
    var minutes =  bknews.nb_rows * bknews.time_height
	+ nbRows * (t.lunch_break_start_time - t.day_start_time
		   + t.day_finish_time - t.lunch_break_finish_time) ;
    if (bknews.nb_rows != 0) {
	minutes += 2 * bknews.time_margin ;
    }
    return minutes ;
}

function scale_from_grid_height(gh) {
    return gh / nb_minutes_in_grid()  ;
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
    return gp.buttxt ;
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
    return p == user.nom ? "tutor-button-me" : "tutor-button-others";
}


/*--------------------
  ------ COURS -------
  --------------------*/
function cours_x(c) {
    return idays[c.day].num * (rootgp_width * labgp.width +
            dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) +
        groups[c.promo][c.group].x * labgp.width;
}

function cours_y(c) {
    var t = time_settings.time ;
    var ret = (c.start-t.day_start_time) * nbRows * scale
	+ row_gp[root_gp[c.promo].row].y * rev_constraints[c.start.toString()] * scale ;
    if (c.start >= t.lunch_break_finish_time) {
	ret += bknews_h() - (t.lunch_break_finish_time - t.lunch_break_start_time)*nbRows*scale ;
    }
    return ret ;
}

function cours_width(c) {
    var gp = groups[c.promo][c.group];
    return (gp.maxx - gp.x) * labgp.width;
}

function cours_height(c) {
    return scale * constraints[c.c_type].duration ;
}

function cours_txt_x(c) {
    return cours_x(c) + .5 * cours_width(c);
}
function cours_txt_fill(c) {
    if (c.id_cours != -1) {
	return c.color_txt;
    }
    return "black";
}
function cours_fill(c) {
    if (c.id_cours != -1) {
	return c.color_bg;
    }
    return "red";
}
function cours_txt_top_y(c) {
    return cours_y(c) + .25 * cours_height(c);
}
function cours_txt_top_txt(c) {
    return c.mod;
}
function cours_txt_mid_y(c) {
    return cours_y(c) + .5 * cours_height(c);
}
function cours_txt_mid_txt(c) {
    return c.prof;
}
function cours_txt_bot_y(c) {
    return cours_y(c) + .75 * cours_height(c);
}
function cours_txt_bot_txt(c) {
    return c.room;
}


/*--------------------
  ------ ROOMS -------
  --------------------*/

function cm_chg_bg_width() {
    return room_tutor_change.cm_settings.mx * (room_tutor_change.cm_settings.ncol + 1 )
	+ room_tutor_change.cm_settings.w * room_tutor_change.cm_settings.ncol ;
}
function cm_chg_bg_height() {
    return room_tutor_change.cm_settings.my * (room_tutor_change.cm_settings.nlin + 1 )
	+ room_tutor_change.cm_settings.h * room_tutor_change.cm_settings.nlin
	+ room_tutor_change.top ;
}

function cm_chg_bg_x() {
    var c = room_tutor_change.course[0] ;
    if (room_tutor_change.posh == 'w') {
	return cours_x(c) + .5 * cours_width(c) - cm_chg_bg_width();
    } else {
	return cours_x(c) + .5 * cours_width(c);
    }
}
function cm_chg_bg_y() {
    var c = room_tutor_change.course[0] ;
    if (room_tutor_change.posv == 's') {
	return cours_y(c)  + .5 * cours_height(c) ;
    } else {
	return cours_y(c)  + .5 * cours_height(c) - cm_chg_bg_height() ;
    }
}

function cm_chg_txt_x() {
    return cm_chg_bg_x() + .5*cm_chg_bg_width() ;
}
function cm_chg_txt_y() {
    return cm_chg_bg_y() + .5*room_tutor_change.top ;
}
function cm_chg_txt() {
    if (Object
	.keys(room_tutor_change.cm_settings.txt_intro)
	.indexOf(room_tutor_change.proposal.length.toString())
	!= -1){
	return room_tutor_change.cm_settings.txt_intro[room_tutor_change.proposal.length.toString()];
    } else {
	return room_tutor_change.cm_settings.txt_intro['default'];
    }
}


function cm_chg_but_width() {
    return room_tutor_change.cm_settings.w ;
}
function cm_chg_but_height() {
    return room_tutor_change.cm_settings.h ;
}

function cm_chg_but_x(d, i) {
    var c = i % room_tutor_change.cm_settings.ncol ;
    var ret = cm_chg_bg_x() + room_tutor_change.cm_settings.mx 
	+ ( room_tutor_change.cm_settings.mx + cm_chg_but_width(d, i) ) * c ;
    return ret ;
}
function cm_chg_but_y(d,i) {
    var l = Math.floor(i/room_tutor_change.cm_settings.ncol) ;
    return cm_chg_bg_y() + room_tutor_change.top + room_tutor_change.cm_settings.my
	+ ( room_tutor_change.cm_settings.my + cm_chg_but_height(d, i) ) * l ;
}

function cm_chg_but_txt_x(d,i) {
    return cm_chg_but_x(d,i) + .5*cm_chg_but_width(d,i) ;
}
function cm_chg_but_txt_y(d,i) {
    return cm_chg_but_y(d,i) + .5*cm_chg_but_height(d,i) ;
}
function cm_chg_but_txt(d,i) {
    return d.content ;
}
function cm_chg_but_stk(d) {
    if (d.content == room_tutor_change.cur_value) {
	return 3 ; 
    } else {
	return 0 ;
    }
}
function cm_chg_but_fill(d){
    if (d.content == room_tutor_change.old_value) {
	return "darkslategrey" ;
    } else {
	return "steelblue" ;
    }
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
    return idays[d.day].num * (did.w + did.mh);
}

function dispot_y(d) {
    var ts = time_settings.time ;
    var ret = 1.25 * valid.h
	+ (d.start_time - ts.day_start_time) * did.scale;
    if(d.start_time>=ts.lunch_break_finish_time) {
	ret -= (ts.lunch_break_finish_time
		- ts.lunch_break_start_time)
	    * did.scale ;
    }
    return ret ;
}

function dispot_w(d) {
    return did.w;
}

function dispot_h(d) {
    return d.duration * did.scale ;
}

function dispot_more_h(d) {
    return  did.shift_s * did.scale;
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
    return dispot_y({start_time:
		     time_settings.time.lunch_break_start_time});
}

function gsclbt_x() {
    return (did.w + did.mh) * days.length - did.mh;
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
  ------- REGEN -----
  ---------------------*/

function ack_reg_y() {
    return grid_height()  + 30 * scale ;
}

/*---------------------
  ------- QUOTE -----
  ---------------------*/

function quote_y() {
    return ack_reg_y() ;
}
function quote_x() {
    return 0 ;
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
