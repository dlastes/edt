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

var margin = {top: tv_svg_top_m, left: 30, right: 0, bot:0};

var svg = {height: tv_svg_h - margin.top - margin.bot, width: tv_svg_w - margin.left - margin.right};

var week = semaine_init ;
var year = an_init;

// filter the right bknews
weeks = {sel: [0], init_data: [{semaine: week, an: year}]};


var labgp = {width: tv_gp_w, tot: 8, height_init: 40, width_init: 30};

scale = tv_gp_s ;

dim_dispo.height = 2*labgp.height ;

dragListener = d3.drag();


pref_only = false ;


/*-------------------
  ------ BUILD ------
  -------------------*/



create_general_svg(true);



file_fetch.groups.callback = function() {

    create_groups(this.data);

    create_edt_grid();

    //    go_promo(promo_display);


    //update_all_groups();


    create_bknews();
    
    go_promo_gp_init();

    fetch_cours_light();
    fetch_bknews_light();
    //adapt_labgp(true);
    fetch.groups_ok = true ;
    //go_edt(true);
    create_grid_data();
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
        url: url_cours_pl + an_att + "/" + semaine_att + "/0",
        async: false,
        contentType: "text/csv",
        success: function (msg, ts, req) {
            days = JSON.parse(req.getResponseHeader('days').replace(/\'/g, '"'));
            
            tutors.pl = [];
            modules.pl = [];
            salles.pl = [];
            
            cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);

	    fetch.ongoing_cours_pl=false;
	    fetch_ended(true);
        },
	error: function(msg) {
	    console.log("error");
	}
    });


}

function fetch_bknews_light(first) {
    fetch.ongoing_bknews = true;
    var semaine_att = week;
    var an_att = year;

    $.ajax({
        type: "GET", //rest Type
        dataType: 'text',
        url: url_bknews + an_att + "/" + semaine_att,
        async: true,
        contentType: "text/json",
        success: function(msg) {
	    bknews.cont = d3.csvParse(msg,
				      translate_bknews_from_csv);
            if (semaine_att == weeks.init_data[weeks.sel[0]].semaine &&
                an_att == weeks.init_data[weeks.sel[0]].an) {
		var max_y = -1 ;
		for (var i = 0 ; i < bknews.cont.length ; i++) {
		    if (bknews.cont[i].y > max_y) {
			max_y = bknews.cont[i].y ;
		    }
		}
		bknews.nb_rows = max_y + 1 ;
		
                fetch.ongoing_bknews = false;
                fetch_ended(true);
            }

        },
        error: function(msg) {
            console.log("error");
            show_loader(false);
        }
    });


}


d3.json(groupes_fi,
 	function(d){ main('groups', d); } );

