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

var user = {
  name: usna,
  dispos: [],
  dispos_bu: [],
  dispos_type: [],
};


dsp_svg.margin = {
  top: tv_svg_top_m,
  left: 30,
  right: 0,
  bot: 0
};

dsp_svg.h = tv_svg_h - dsp_svg.margin.top - dsp_svg.margin.bot;
dsp_svg.w = tv_svg_w - dsp_svg.margin.left - dsp_svg.margin.right;

var week = week_init;
var year = year_init;

// filter the right bknews

wdw_weeks.add_full_weeks([{ week: week, year: year }]);

var days_header = new WeekDayHeader(svg, "edt-fg", week_days, true, null);

var hours_header = new HourHeader(svg, "edt-fg", hours);


var labgp = { width: tv_gp_w, tot: 8, height_init: 40, width_init: 30 };

scale = tv_gp_s;

dim_dispo.height = 2 * labgp.height;

dragListener = d3.drag();


pref_only = false;


/*-------------------
  ------ BUILD ------
  -------------------*/

// to be cleaned!
dsp_svg.cadastre = [
  // menus ground
  ["svg", "meg"],
  // weeks ground
  ["svg", "wg"],
  ["wg", "wg-bg"],
  ["wg", "wg-fg"],
  // selection categories button ground
  ["svg", "catg"],
  // semaine type ground
  ["svg", "stg"],
  // dispos info ground
  ["svg", "dig"],
  // valider
  ["svg", "vg"],
  // background, middleground, foreground, dragground
  ["svg", "edtg"],
  ["edtg", "edt-bg"],
  ["edtg", "edt-mg"],
  ["edtg", "edt-fig"],
  ["edtg", "edt-fg"],
  // selection ground
  ["svg", "selg"],
  // context menus ground
  ["svg", "cmg"],
  ["cmg", "cmpg"],
  ["cmg", "cmtg"],
  // drag ground
  ["svg", "dg"]
];



svg = new Svg(dsp_svg.layout_tree, true);
svg.create_container();
svg.create_layouts(dsp_svg.cadastre);



file_fetch.groups.callback = function () {

  create_groups(this.data);

  create_edt_grid();

  //    go_promo(promo_display);


  //update_all_groups();


  create_bknews();

  go_promo_gp_init();

  fetch_cours_light();
  fetch_bknews_light();
  //adapt_labgp(true);
  fetch.groups_ok = true;
  //go_edt(true);
  create_grid_data();
};



function fetch_cours_light() {
  fetch.ongoing_cours_pl = true;
  fetch.cours_ok = false;

  fetch.done = false;
  ack.edt = "";

  var week_att = week;
  var year_att = year;

  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: url_cours_pl + year_att + "/" + week_att + "/0",
    async: false,
    contentType: "text/csv",
    success: function (msg, ts, req) {
      days = JSON.parse(req.getResponseHeader('days').replace(/'/g, '"'));

      tutors.pl = [];
      modules.pl = [];
      salles.pl = [];

      cours_pl = d3.csvParse(msg, translate_cours_pl_from_csv);

      fetch.ongoing_cours_pl = false;
      fetch_ended(true);
    },
    error: function (msg) {
      console.log("error");
    }
  });


}

function fetch_bknews_light(first) {
  fetch.ongoing_bknews = true;
  var exp_week = new Week(year, week);

  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: url_bknews + year_att + "/" + week_att,
    async: true,
    contentType: "text/json",
    success: function (msg) {
      //console.log(msg);

      bknews.cont = JSON.parse(msg);

      var sel_week = wdw_weeks.get_selected();
      if (Week.compare(sel_week, exp_week) == 0) {
        var max_y = -1;
        for (var i = 0; i < bknews.cont.length; i++) {
          if (bknews.cont[i].y > max_y) {
            max_y = bknews.cont[i].y;
          }
        }
        bknews.nb_rows = max_y + 1;

        fetch.ongoing_bknews = false;
        fetch_ended(true);
      }

    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });


}

d3.json(rooms_fi,
  function (d) { main('rooms', d); });

d3.json(constraints_fi,
  function (d) { main('constraints', d); });

d3.json(departments_fi,
  function (d) { main('department', d); });

d3.json(groupes_fi,
  function (d) { main('groups', d); });

