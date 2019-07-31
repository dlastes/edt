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

var user = {nom: usna,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: [],
	   };


dsp_svg.margin = {top: tv_svg_top_m,
                  left: 30,
                  right: 0,
                  bot:0};

dsp_svg.h = tv_svg_h - dsp_svg.margin.top - dsp_svg.margin.bot ;
dsp_svg.w = tv_svg_w - dsp_svg.margin.left - dsp_svg.margin.right ;

var week = semaine_init ;
var year = an_init;

// filter the right bknews

var week_banner = new WeekBanner(svg, "wg", "wg-fg", "wg-bg", wdw_weeks, dsp_weeks);
week_banner.spawn([{semaine: week, an: year}]) ;

var days_header = new WeekDayHeader(svg, "edt-fg", week_days, true, null) ;

var labgp = {height: tv_gp_h, width: tv_gp_w, tot: 8, height_init: 40, width_init: 30};

dim_dispo.height = 2*labgp.height ;

dragListener = d3.drag();


pref_only = false ;


/*-------------------
  ------ BUILD ------
  -------------------*/

// to be cleaned!
dsp_svg.cadastre = [
    // menus ground
    ["svg","meg"],
    // weeks ground
    ["svg","wg"],
    ["wg","wg-bg"],
    ["wg","wg-fg"],
    // selection categories button ground
    ["svg","catg"],
    // semaine type ground
    ["svg","stg"],
    // dispos info ground
    ["svg","dig"],
    // valider
    ["svg","vg"],
    // background, middleground, foreground, dragground
    ["svg","edtg"],
    ["edtg","edt-bg"],
    ["edtg","edt-mg"],
    ["edtg","edt-fig"],
    ["edtg","edt-fg"],
    // selection ground
    ["svg","selg"],
    // context menus ground
    ["svg","cmg"],
    ["cmg","cmpg"],
    ["cmg","cmtg"],
    // drag ground
    ["svg","dg"]
];



svg = new Svg(dsp_svg.layout_tree, true);
svg.create_container();
svg.create_layouts(dsp_svg.cadastre);


d3.json(groupes_fi,
 	on_group_rcv_light);



function on_group_rcv_light(dg) {

    create_groups(dg);

//    go_promo(promo_display);
    go_promo_gp_init();
    update_all_groups();

    create_edt_grid();

    create_bknews();
    

    fetch_cours_light();
    fetch_bknews_light();
    //go_edt(true);
}



function fetch_cours_light() {
    fetch.ongoing_cours_pl  = true ;
    fetch.cours_ok  = false;

    fetch.done = false ;
    ack.edt="";
    
    var semaine_att = week;
    var an_att = year;

    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_cours_pl+"/"+an_att+"/"+semaine_att+"/0",
        async: false,
        contentType: "text/csv",
        success: function (msg, ts, req) {
	    version = +req.getResponseHeader('version');

	    
	    var day_arr = JSON.parse(req.getResponseHeader('jours').replace(/\'/g,'"'));
	    for (var i =0 ; i<day_arr.length ; i++){
	    	data_grid_scale_day[i] = data_grid_scale_day_init[i]+ " "+day_arr[i];
	    }
	    
	    cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);
	    
	    
	    fetch.ongoing_cours_pl=false;
	    fetch_ended_light();
        },
	error: function(msg) {
	    console.log("error");
	}
    });


}

function fetch_bknews_light(first) {
    fetch.ongoing_bknews = true;
    var exp_week = new Week(year, week) ;

    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_bknews + an_att + "/" + semaine_att,
        async: true,
        contentType: "text/json",
        success: function(msg) {
            //console.log(msg);

            bknews.cont = JSON.parse(msg) ;

            var sel_week = week_banner.get_selected() ;
            if (Week.compare(sel_week, exp_week)==0) {
		var max_y = -1 ;
		for (var i = 0 ; i < bknews.cont.length ; i++) {
		    if (bknews.cont[i].y > max_y) {
			max_y = bknews.cont[i].y ;
		    }
		}
		bknews.nb_rows = max_y + 1 ;

		//adapt_labgp(first);
		// if (first) {
		//     create_but_scale();

		// }

		
		
                fetch.ongoing_bknews = false;
                fetch_ended_light();
            }
        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });


}



function fetch_ended_light() {
    if(!fetch.ongoing_cours_pl &&
       !fetch.ongoing_cours_pp){
	cours = cours_pl.concat(cours_pp);
	clean_prof_displayed();
	fetch.cours_ok=true;
    }
    
    if (!fetch.ongoing_cours_pp &&
	!fetch.ongoing_cours_pl &&
	!fetch.ongoing_dispos &&
        !fetch.ongoing_bknews){
	fetch.done = true ;

	go_grid(true);
	go_courses(true);
	go_bknews(true);
    }

    svg.add_child("svg", "final");

}
