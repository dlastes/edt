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

/*-------------------
  ---- VARIABLES ----
  -------------------*/

var user = {nom: logged_usr.nom,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: []
	   };

var margin = {
    top: 250,     // - TOP BANNER - //
    left:  50,
    right:  110,
    bot:  10,
    but: -230
};


var bs_margin_w = 20 ;
var bs_margin_h = 5 ;

var svg = {
    height: window.innerHeight - $("#menu-edt").height() - bs_margin_h,
    width: window.innerWidth - bs_margin_w,
};


var week = 42 ;
var year = 2017;

var labgp = {height: 40, width: 30, tot: 8, height_init: 40, width_init: 30, hm: 40, wm:15};

var dim_dispo = {height:2*labgp.height, width: 60, right: 10, plot:0,
		 adv_v_margin: 5};


butgp.tly = margin.but;//-margin_but.ver-6*butgp.height-80 ;
butpr.tly = margin.but;


modules.x=butpr.tlx+butpr_x(null,butpr.perline-2)+butpr.width+butpr.mar_x-60;
modules.y=margin.top+gsckd_y(null)-40;
modules.width = 170 ;
modules.height = 0 ;


salles.x=modules.x-1.2*modules.width ; //5*butpr.width;
salles.y=modules.y-modules.height;//.6*butpr.height;
salles.width = 150 ; 
salles.height = modules.height ; 


/*-------------------
  ------ BUILD ------
  -------------------*/



create_general_svg(false);

def_drag();
create_clipweek();
create_menus();
create_forall_prof();


fetch_dispos_type();


d3.json(groupes_fi,
 	on_group_rcv);



d3.select("body")
    .on("click", function(d) {if(ckbox["dis-mod"].cked) {
	if(dispo_menu_appeared) {
	    del_dispo_adv = true ;
	    dispo_menu_appeared = false ;
	    go_dispos(true);
	} else {
	    if(del_dispo_adv) {
		del_dispo_adv = false ;
		data_dispo_adv_cur = [] ;
		go_dispos(true);
	    }
	}
    }})



