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
-------    CREATION    -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */



/*---------------------------
  ------- PREFERENCES -------
  ---------------------------*/

function create_alarm_dispos() {
  di = svg.get_dom("dig")
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


function create_pref_modes() {

  pref_selection.choice.data.forEach(function (d) {
    d.selected = false;
  });

  svg.get_dom("pmg")
    .attr("transform", pmg_trans());

  var buttons = svg.get_dom("pmg")
    .append("g")
    .attr("id", "pm-but-head")
    .attr("transform", pref_mode_trans());

  var choices_but = svg.get_dom("pmg")
    .append("g")
    .attr("id", "pm-choices")
    .attr("transform", pref_mode_choice_trans());

  go_pref_mode();
}


function remove_pref_modes() {
  svg.get_dom("pmg").selectAll("*").remove();
}

/*---------------------
  ------- WEEKS -------
  ---------------------*/








/*----------------------
  -------- GRID --------
  ----------------------*/


// PRE: groups
function create_edt_grid() {
  create_grid_data();
  //go_grid(false);
}



function add_garbage() {

  if (slot_case) {

    var garbage_dsg = {
      day: garbage.day,
      start: garbage.start,
      duration: rev_constraints[garbage.start],
      display: false,
      dispo: false,
      pop: false,
      reason: ""
    };

    data_slot_grid.push(garbage_dsg);

  }
}
function remove_garbage() {
  var found = false;
  var i = 0;
  while (!found && i < data_slot_grid.length) {
    if (data_slot_grid[i].day == garbage.day
      && data_slot_grid[i].slot == garbage.slot) {
      found = true;
      data_slot_grid.splice(i, 1);
    }
    i += 1;
  }
}


// create potential slots for course c
function create_slot_grid_data(c) {
  data_slot_grid = [];
  if (slot_case) {
    // does not depend on course c

    week_days.forEach(function (day) {
      for (var s in rev_constraints) {
        var start = +s;
        if (start < time_settings.time.day_finish_time) {
          var gs = {
            day: day.ref,
            start: start,
            duration: rev_constraints[s],
            display: false,
            dispo: false,
            pop: false,
            reason: ""
          };
          data_slot_grid.push(gs);
        }
      }
    });
  } else {
    var ok_starts = constraints[c.c_type].allowed_st;
    week_days.forEach(function (day) {
      for (var s = 0; s < ok_starts.length; s++) {
        data_slot_grid.push({
          c_type: c.c_type,
          day: day.ref,
          group: c.group,
          promo: c.promo,
          start: ok_starts[s],
          duration: c.duration
        });
      }
    });
  }
}


function create_grid_data() {
  if (fetch.constraints_ok && fetch.groups_ok) {
    if (slot_case) {
      create_slot_grid_data();
    }

    for (let p = 0; p < set_promos.length; p++) {
      compute_promo_leaves(root_gp[p].gp);
    }


    if (slot_case) {
      for (let s = 0; s < Object.keys(rev_constraints).length; s++) {
        for (let r = 0; r < set_rows.length; r++) {
          var start = Object.keys(rev_constraints)[s];
          if (start < time_settings.time.day_finish_time) {
            var gscp = {
              row: r,
              start: start,
              duration: rev_constraints[start],
              name: set_promos_txt[row_gp[r].promos[0]]
            };
            for (let p = 1; p < row_gp[r].promos.length; p++) {
              gscp.name += "|";
              gscp.name += set_promos_txt[row_gp[r].promos[p]];
            }
            data_grid_scale_row.push(gscp);
          }
        }
      }
    }

  }
}


/*----------------------
  -------- SCALE -------
  ----------------------*/

function create_but_scale() {
  def_drag_sca();

  var grp = svg.get_dom("edt-fg")
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



  grp = svg.get_dom("edt-fg")
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
    .on("start", function (c) {
      if (fetch.done) {
        drag.sel = d3.select(this);
        drag.x = 0;
        drag.y = 0;
        drag.svg = d3.select("#edt-main");
        drag.svg_w = +drag.svg.attr("width");
        drag.init = +drag.sel.select("rect").attr("x");
        svg.get_dom("dg").node().appendChild(drag.sel.node());


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
    .on("drag", function (c) {
      if (fetch.done) {
        drag.x += d3.event.dx;
        if (drag.x + drag.init > 0) {
          drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
          if (drag.init + drag.x + dsp_svg.margin.left + dsp_svg.margin.right > drag.svg_w) {
            drag.svg.attr("width", drag.init + drag.x + dsp_svg.margin.left + dsp_svg.margin.right);
          }
        }
      }
    })
    .on("end", function (c) {
      if (fetch.done) {
        if (drag.x + drag.init <= 0) {
          drag.x = -drag.init;
        }
        drag.sel.attr("transform", "translate(0,0)");
        drag.sel.select("rect").attr("x", drag.init + drag.x);
        if (rootgp_width != 0) {
          labgp.width = ((drag.x + drag.init) / week_days.nb_days() - dim_dispo.plot * (dim_dispo.width + dim_dispo.right)) / rootgp_width;
        }
        drag.sel.select("path").attr("d", but_sca_tri_h(0));
        //(drag.x+drag.init)/(grid_width());
        go_edt(false);
        svg.get_dom("edt-fg").node().appendChild(drag.sel.node());
        drag.sel.select(".h-sca-l").remove();
      }
    });

  drag_listener_vs = d3.drag()
    .on("start", function (c) {
      if (fetch.done) {
        drag.sel = d3.select(this);
        drag.x = 0;
        drag.y = 0;
        drag.init = +drag.sel.select("rect").attr("y");
        svg.get_dom("dg").node().appendChild(drag.sel.node());
        drag.svg = d3.select("#edt-main");
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
    .on("drag", function (c) {
      if (fetch.done) {
        drag.y += d3.event.dy;
        if (drag.init + drag.y >= 0) {
          drag.sel.attr("transform",
            "translate(" + drag.x + "," + drag.y + ")");
          drag.svg.attr("height", drag.svg_h + drag.y);
        }
      }
    })
    .on("end", function (c) {
      if (fetch.done) {
        if (drag.init + drag.y < 0) {
          drag.y = -(drag.init);
        }
        scale = scale_from_grid_height(drag.init + drag.y);
        drag.sel.attr("transform", "translate(0,0)");
        drag.sel.select("rect").attr("y", grid_height());
        drag.sel.select("path").attr("d", but_sca_tri_v(0));
        go_edt(false);
        svg.get_dom("edt-fg").node().appendChild(drag.sel.node());
        drag.sel.select(".v-sca-l").remove();

        dsp_svg.h = svg_height();
        d3.select("#edt-main").attr("height", dsp_svg.h);

      }
    });

}



/*----------------------
  ------- GROUPS -------
  ----------------------*/

// Only for the current case
function set_butgp() {
  var topx = 0;//615 + 4*30;

  var cur_buty = 0;
  var cur_rootgp;
  for (var nrow = 0; nrow < set_rows.length; nrow++) {
    var cur_maxby = 0;
    var tot_row_gp = 0;
    var cur_butx = topx;

    for (var npro = 0; npro < row_gp[nrow].promos.length; npro++) {
      cur_rootgp = root_gp[row_gp[nrow].promos[npro]];
      cur_rootgp.buty = cur_buty;
      if (cur_rootgp.maxby > cur_maxby) {
        cur_maxby = cur_rootgp.maxby;
      }
      tot_row_gp += cur_rootgp.gp.width * butgp.width;
      tot_row_gp += (npro == 0) ? 0 : (butgp.mar_h);
      // console.log(cur_rootgp.gp.width, butgp.width);
      cur_rootgp.butx = cur_butx;
      cur_butx += butgp.mar_h + cur_rootgp.gp.width * butgp.width;
    }
    cur_buty += butgp.mar_v + cur_maxby * butgp.height;
  }


  // Compute dimensions of the group selection popup

  var minx, maxx, miny, maxy, curminx, curmaxx, curminy, curmaxy, curp;

  for (var p = 0; p < set_promos.length; p++) {
    curp = root_gp[p];
    curminx = curp.butx;
    curminy = curp.buty;
    if (p == 0 || curminx < minx) {
      minx = curminx;
    }
    if (p == 0 || curminy < miny) {
      miny = curminy;
    }
    curmaxx = curminx + curp.gp.bw * butgp.width;
    curmaxy = curminy + curp.maxby * butgp.height;
    if (p == 0 || curmaxx > maxx) {
      maxx = curmaxx;
    }
    if (p == 0 || curmaxy > maxy) {
      maxy = curmaxy;
    }
  }

  sel_popup.groups_w = maxx - minx;
  sel_popup.groups_h = maxy - miny;

}



function indexOf_promo(promo) {
  for (var p = 0; p < set_promos.length; p++) {
    if (set_promos[p] == promo_init) {
      return p;
    }
  }
  return -1;
}

function go_promo_gp_init(button_available) {
  var gp_2_click = [];
  var found_gp, gpk, gpc, gpa;

  promo_init = indexOf_promo(promo_init);
  if (promo_init >= 0) {
    if (gp_init == "") {
      gp_init = root_gp[promo_init].gp.name;
    }
    if (Object.keys(groups[promo_init]).map(function (g) { return groups[promo_init][g].name; }).indexOf(gp_init) != -1) {
      apply_gp_display(groups[promo_init][gp_init], true, button_available);
    }
  } else if (gp_init != "") {
    if (Object.keys(groups[0]).map(function (g) { return groups[0][g].name; }).indexOf(gp_init) != -1) {
      apply_gp_display(groups[0][gp_init], true, button_available);
    }
  }
}


function create_groups(data_groups) {
  var root;

  extract_all_groups_structure(data_groups);

  for (let r = 0; r < set_rows.length; r++) {
    for (let p = 0; p < row_gp[r].promos.length; p++) {
      root = root_gp[row_gp[r].promos[p]].gp;
      create_static_att_groups(root);
    }
  }

  update_all_groups();

  for (let r = 0; r < set_rows.length; r++) {
    for (let p = 0; p < row_gp[r].promos.length; p++) {
      root = root_gp[row_gp[r].promos[p]];
      root.minx = root.gp.x;
    }
  }
  for (let p = 0; p < set_promos.length; p++) {
    var keys = Object.keys(groups[p]);
    for (let g = 0; g < keys.length; g++) {
      groups[p][keys[g]].bx = groups[p][keys[g]].x;
      groups[p][keys[g]].bw = groups[p][keys[g]].width;
    }
  }

  set_butgp();
}


function extract_all_groups_structure(r) {
  var init_nbPromos = r.length;
  for (let npro = 0; npro < init_nbPromos; npro++) {
    extract_groups_structure(r[npro], -1, -1);
  }
  var sorted_rows = set_rows.sort();
  for (let npro = 0; npro < set_promos.length; npro++) {
    root_gp[npro].row = sorted_rows.indexOf(set_rows[root_gp[npro].row]);
  }
  set_rows = sorted_rows;
}

function extract_groups_structure(r, npro, nrow) {
  var gr = {
    name: r.name,
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
  };

  if ("undefined" === typeof r.buth) {
    gr.buth = 1;
  } else {
    gr.buth = r.buth * .01;
  }

  if ("undefined" === typeof r.buttxt) {
    gr.buttxt = gr.name;
  } else {
    gr.buttxt = r.buttxt;
  }


  if (r.parent == "null") {

    // promo number should be unique
    set_promos.push(r.promo);
    set_promos_txt.push(r.promotxt);

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
    gr.children = r.children.map(function (d) {
      return d.name;
    });
    for (var i = 0; i < r.children.length; i++) {
      extract_groups_structure(r.children[i], npro, nrow);
    }
  }
  groups[npro][gr.name] = gr;
}



function create_static_att_groups(node) {
  var child;

  if (node.parent == null) {
    node.by = 0;
    root_gp[node.promo].maxby = node.by + node.buth;
  } else {
    if (node.by + node.buth > root_gp[node.promo].maxby) {
      root_gp[node.promo].maxby = node.by + node.buth;
    }
  }
  node.descendants = [];


  if (node.children.length != 0) {
    for (var i = 0; i < node.children.length; i++) {
      child = groups[node.promo][node.children[i]];
      child.by = node.by + node.buth;
      create_static_att_groups(child);
    }
  }

}


// Earliest Starting Time (i.e. leftest possible position)
// for a node and its descendance, given node.est
function compute_promo_est_n_wh(node) {
  var child;


  if (node.parent == null) {
    node.ancetres = [];
  }
  node.descendants = [];


  node.width = 0;
  if (node.children.length == 0) {
    if (node.display) {
      node.width = 1;
    } else {
      node.width = 0;
    }
  } else {
    for (var i = 0; i < node.children.length; i++) {
      child = groups[node.promo][node.children[i]];
      child.est = node.est + node.width;
      if (!child.display) {
        child.width = 0;
      } else {
        child.ancetres = node.ancetres.slice(0);
        child.ancetres.push(node.name);
        compute_promo_est_n_wh(child);
        node.descendants = node.descendants.concat(child.descendants);
        node.descendants.push(child.name);
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

  //    console.log(node.promo,node.name,node.x,node.maxx);

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
}



function update_all_groups() {
  var max_rw = 0;
  var cur_rw, root, disp;

  // compute EST and width, and compute display row
  for (let r = 0; r < set_rows.length; r++) {
    cur_rw = 0;
    disp = false;
    for (let p = 0; p < row_gp[r].promos.length; p++) {
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

  // should not occur; can occur when there is no group in the department
  if (rootgp_width == 0) {
    rootgp_width = 5;
  }

  if (pos_rootgp_width == 0) {
    pos_rootgp_width = rootgp_width;
  }
  labgp.width *= pos_rootgp_width / rootgp_width;
  pos_rootgp_width = rootgp_width;



  // compute LFT
  for (let r = 0; r < set_rows.length; r++) {
    cur_rw = max_rw;
    for (let p = row_gp[r].promos.length - 1; p >= 0; p--) {
      root = root_gp[row_gp[r].promos[p]].gp;
      root.lft = cur_rw;
      compute_promo_lft(root);
      cur_rw -= root.width;
    }
  }
  // move x if necessary
  for (let r = 0; r < set_rows.length; r++) {
    cur_rw = 0;
    for (let p = 0; p < row_gp[r].promos.length; p++) {
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
  for (let r = 0; r < set_rows.length; r++) {
    root = row_gp[r];
    root.display = false;
    root.y = nbRows;
    for (let p = 0; p < row_gp[r].promos.length; p++) {
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
    scale *= pos_nbRows / nbRows;
    pos_nbRows = nbRows;
  }
}



// data related to leaves
function compute_promo_leaves(node) {
  var gp;

  if (node.children.length == 0) {
    week_days.forEach(function (day) {
      data_grid_scale_gp.push({
        day: day.num,
        gp: node
      });
    });
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

  svg.get_dom("meg")
    .attr("transform", "translate(" + menus.x + "," + menus.y + ")")
    .attr("text-anchor", "start");

  svg.get_dom("meg")
    .append("rect")
    .attr("class", "menu")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", menus.coled + menus.colcb)
    .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
    .attr("rx", 10)
    .attr("ry", 10);

  svg.get_dom("meg")
    .append("rect")
    .attr("class", "menu")
    .attr("x", menus.dx)
    .attr("y", 0)
    .attr("width", menus.coled + menus.colcb)
    .attr("height", 160) //(Object.keys(ckbox).length+1)*menus.h)
    .attr("rx", 10)
    .attr("ry", 10);

  svg.get_dom("meg")
    .append("text")
    .attr("x", menus.mx)
    .attr("y", menus.h - 10)
    .attr("fill", "black")
    .text("Cours :");

  svg.get_dom("meg")
    .append("text")
    .attr("x", menus.mx + menus.dx)
    .attr("y", menus.h - 10)
    .attr("fill", "black")
    .text("Dispos :");

  go_menus();
}



/*---------------------
  ------- BKNEWS ------
  ---------------------*/

function create_regen() {
  svg.get_dom("vg")
    .append("g")
    .attr("class", "ack-reg")
    .append("text");
}




function create_bknews() {
  var flash = svg.get_dom("edt-fig")
    .append("g")
    .attr("class", "flashinfo");


  flash
    .append("line")
    .attr("class", "bot-bar")
    .attr("stroke", "black")
    .attr("stroke-width", 4)
    .attr("x1", 0)
    .attr("y1", bknews_bot_y())
    .attr("x2", grid_width())
    .attr("y2", bknews_bot_y());

  flash
    .append("line")
    .attr("class", "top-bar")
    .attr("stroke", "black")
    .attr("stroke-width", 4)
    .attr("x1", 0)
    .attr("y1", bknews_top_y())
    .attr("x2", grid_width())
    .attr("y2", bknews_top_y());

  var fl_txt = flash
    .append("g")
    .attr("class", "txt-info");



}


/*---------------------
  ------- QUOTES ------
  ---------------------*/

function create_quote() {
  svg.get_dom("vg")
    .append("g")
    .attr("class", "quote")
    .append("text");

  show_loader(true);
  $.ajax({
    type: "GET", //rest Type
    dataType: 'text',
    url: url_quote,
    async: true,
    contentType: "text/csv",
    success: function (msg) {
      // console.log(msg);

      var quotes = d3.csvParse(msg, translate_quote_from_csv);
      if (quotes.length > 0) {
        quote = quotes[0];
      } else {
        quote = '';
      }

      svg.get_dom("vg").select(".quote").select("text")
        .text(quote);


      show_loader(false);

    },
    error: function (msg) {
      console.log("error");
      show_loader(false);
    }
  });
}

function translate_quote_from_csv(d) {
  return d.txt;
}



/*----------------------
   ------ COURSES ------
  ----------------------*/


function def_drag() {
  var cur_over = null;
  var slots_over = null;
  dragListener = d3.drag()
    .on("start", function (c) {
      cancel_cm_adv_preferences();
      cancel_cm_room_tutor_change();
      if (ckbox["edt-mod"].cked && fetch.done) {

        if (!slot_case) {
          create_slot_grid_data(c);
        }

        // no data_slot_grid when uniline
        data_slot_grid.forEach(function (sl) {
          fill_grid_slot(c, sl);
        });


        drag.x = 0;
        drag.y = 0;

        // raise the course to the drag layer
        drag.sel = d3.select(this);
        svg.get_dom("dg").node().appendChild(drag.sel.node());

      }
    })
    .on("drag", function (d) {
      if (ckbox["edt-mod"].cked && fetch.done) {
        pending.prepare_dragndrop(d);
        cur_over = which_slot(
          drag.x + parseInt(drag.sel.select("rect").attr("x")),
          drag.y + parseInt(drag.sel.select("rect").attr("y")),
          d);
        //console.log(cur_over.day, cur_over.start_time);

        data_slot_grid.forEach(function (s) {
          s.display = false;
        });
        if (!is_garbage(cur_over)) {
          slots_over = data_slot_grid.filter(function (c) {
            return c.day == cur_over.day
              && c.start == cur_over.start_time;
          });
          slots_over.forEach(function (s) {
            s.display = true;
          });
        }
        go_grid(true);

        drag.x += d3.event.dx;
        drag.y += d3.event.dy;
        drag.sel.attr("transform", "translate(" + drag.x + "," + drag.y + ")");
      }
    })
    .on("end", function (d) {

      // click => end. So if real drag
      if (drag.sel != null) {

        // lower the course to the middleground layer
        svg.get_dom("edt-mg").node().appendChild(drag.sel.node());

        if (cur_over != null && ckbox["edt-mod"].cked && fetch.done) {


          if (slot_case) {
            data_slot_grid.forEach(function (s) {
              s.display = false;
            });
          } else {
            data_slot_grid = [];
          }


          if (!is_garbage(cur_over)) {

            // console.log("not garbage");

            // var gs = data_slot_grid.filter(function(s) {
            //     return s.day == cur_over.day
            // 	    && s.start == cur_over.start_time;
            // });

            var pending_change = {
              day: cur_over.day,
              start: cur_over.start_time
            };
            console.log(pending.init_course.start);

            // Object.assign(d,pending_change) ;
            // console.log(pending.init_course.start);
            // pending.wanted_course = Object.assign({},d) ;

            Object.assign(pending.wanted_course, pending_change);

            check_pending_course();

          } else {
            d.day = cur_over.day;
            d.start = cur_over.start_time;

            add_bouge(pending.init_course);
            pending.clean();
          }

          drag.sel.attr("transform", "translate(0,0)");

          drag.x = 0;
          drag.y = 0;
          drag.sel = null;
          cur_over = null;

          go_grid(true);
          go_courses(true);
        }
      }
    });

  drag_popup = d3.drag()
    .on("start", function (d) {
      drag.sel = d3.select(this);
      drag.sel.raise();
    })
    .on("drag", function (d) {
      d.x += d3.event.dx;
      d.y += d3.event.dy;
      drag.sel.attr("transform", popup_trans(d));
    })
    // save panel position
    .on("end", function (d) {
      var infos = sel_popup.get_available(d.type);
      if (typeof infos !== 'undefined') {
        infos.x = d.x;
        infos.y = d.y;
      }
      drag.sel = null;
    });
}




function fill_grid_slot(c2m, grid_slot) {
  grid_slot.dispo = true;
  grid_slot.reason = "";

  // // the user has the right to do whatever s/he wants
  // if ((logged_usr.rights >> 2) % 2 == 1) {
  // 	return ;
  // }
  var wanted_course = Object.assign({}, c2m);
  Object.assign(wanted_course, { day: grid_slot.day, start: grid_slot.start });

  var check = check_course(wanted_course);

  if (check.length == 0) {
    return;
  } else {
    grid_slot.dispo = false;
    if (check.nok_type == 'stable') {
      grid_slot.reason = "Cours fixe";
    } else if (check.nok_type == 'train_prog_unavailable') {
      grid_slot.reason = "CRENEAU NON DISPO POUR " + check.train_prog;
    } else if (check.nok_type == 'tutor_busy') {
      grid_slot.reason = "PB PROF OCCUPE";
    } else if (check.nok_type == 'group_busy') {
      grid_slot.reason = "PB GROUPE";
    } else if (check.nok_type == 'tutor_unavailable') {
      grid_slot.reason = "PB PROF PAS DISPO";
    } else if (check.nok_type == 'tutor_availability_unknown') {
      grid_slot.reason = "PB DISPO NON DECLAREE";
    }
    return;
  }

}

function warning_check(check_tot) {
  var ret = [];
  ret = check_tot.map(function (check) {
    var expand;
    if (check.nok == 'stable') {
      expand = "Le cours était censé être fixe.";
    } else if (check.nok == 'train_prog_unavailable') {
      expand = "La promo " + check.more.train_prog + " ne devait pas avoir cours à ce moment-là.";
    } else if (check.nok == 'tutor_busy') {
      expand = "L'enseignant·e " + check.more.tutor + " avait déjà un cours prévu.";
    } else if (check.nok == 'group_busy') {
      expand = "Le groupe " + check.more.group + " avait déjà un cours prévu.";
    } else if (check.nok == 'tutor_unavailable') {
      expand = "L'enseignant·e " + check.more.tutor + " s'était déclaré·e indisponible.";
    } else if (check.nok == 'tutor_availability_unknown') {
      expand = "L'enseignant·e " + check.more.tutor + " n'a pas déclaré ses dispos.";
    } else if (check.nok == 'tutor_busy_other_dept') {
      expand = "L'enseignant·e " + check.more.tutor + " est occupé dans un autre département.";
    } else if (check.nok == 'tutor_free_week') {
      expand = "L'enseignant·e " + check.more.tutor + " ne donne pas de cours cette week.";
    } else if (check.nok == 'room_busy') {
      if (check.more.rooms.length == 1) {
        expand = "La salle " + check.more.rooms[0] + " est déjà prise.";
      } else {
        expand = "Les salles " + check.more.rooms.join(", ") + " sont déjà prises.";
      }
    } else if (check.nok == 'room_busy_other_dept') {
      expand = "La salle " + check.more.room + " est utilisée par un autre département.";
    }
    return expand;
  });
  return ret;
}


// return all simultaneous courses
function simultaneous_courses(target_course) {
  return cours.filter(function (c) {
    return (c.day == target_course.day
      && !(c.start + c.duration <= target_course.start
        || c.start >= target_course.start + target_course.duration)
      && c.id_course != target_course.id_course);
  });
}

/*
 check whether it is possible to schedule c2m on time date.start_time, day date.day. 
 returns an object containing at least contraints_ok: true iff it is, and
 - nok_type: 'stable' -> course cannot be moved
 - nok_type: 'train_prog_unavailable', train_prog: abbrev_train_prog -> students
   from training programme abbrev_train_prog are not available
 - nok_type: 'tutor_busy', tutor: tutor_username -> the tutor has already
   another course
 - nok_type: 'group_busy', group: gp_name -> the group has already another course
 - nok_type: 'tutor_unavailable', tutor: tutor_username -> the tutor is 
   unavailable
 - nok_type: 'sleep', tutor: tutor_username -> the tutor needs to sleep (11h break)
*/
// c2m element of course
// date {day, start_time}
function check_course(wanted_course) {

  var ret = [];
  var possible_conflicts = [];
  var conflicts = [];

  if (is_garbage(wanted_course)) {
    return ret;
  }

  if (cosmo) {
    pending.pass.room = true;
  }

  if (!pending.pass.core) {

    // course was supposed to be fix
    if (wanted_course.id_course == -1) {
      ret.push({ nok: 'stable' });
    }

    // training programme was supposed to be free
    if (is_free(wanted_course, wanted_course.promo)) {
      ret.push({
        nok: 'train_prog_unavailable',
        more: { train_prog: set_promos[wanted_course.promo] }
      });
    }
  }




  possible_conflicts = simultaneous_courses(wanted_course);

  if (!pending.pass.core) {

    // group is busy
    conflicts = possible_conflicts.filter(function (c) {
      return ((c.group == wanted_course.group
        || groups[wanted_course.promo][wanted_course.group].ancetres.indexOf(c.group) > -1
        || groups[wanted_course.promo][wanted_course.group].descendants.indexOf(c.group) > -1)
        && c.promo == wanted_course.promo);
    });

    if (conflicts.length > 0) {
      ret.push({
        nok: 'group_busy',
        more: { group: wanted_course.group }
      });
    }

    // we will ask later about other constraints
    if (ret.length > 0 && (pending.force.tutor || pending.force.room)) {
      return ret;
    }

  }



  // tutor availability
  if (!pending.pass.tutor) {
    conflicts = possible_conflicts.filter(function (c) {
      return (c.prof == wanted_course.prof);
    });



    if (conflicts.length > 0) {
      ret.push({
        nok: 'tutor_busy',
        more: { tutor: wanted_course.prof }
      });
    }



    // tutor availability
    if (dispos[wanted_course.prof] !== undefined) {

      // in the current department
      var pref_tut = get_preference(dispos[wanted_course.prof][wanted_course.day],
        wanted_course.start, wanted_course.duration);
      if (pref_tut == 0) {
        ret.push({
          nok: 'tutor_unavailable',
          more: { tutor: wanted_course.prof }
        });
      } else if (pref_tut == -1) {
        ret.push({
          nok: 'tutor_availability_unknown',
          more: { tutor: wanted_course.prof }
        });
      }

      // in other departments
      var extra_unavailable = find_in_pref(extra_pref.tutors, wanted_course.prof, wanted_course);

      if (extra_unavailable == 0) {
        ret.push({
          nok: 'tutor_busy_other_dept',
          more: { tutor: wanted_course.prof }
        });
      }

    } else {
      ret.push({
        nok: 'tutor_free_week',
        more: { tutor: wanted_course.prof }
      });
    }

    // we will ask later about room constraints
    if (ret.length > 0 && pending.force.room) {
      return ret;
    }


  }

  // shared rooms availability
  // var extra_unavailable = find_in_pref(extra_pref.rooms,
  //                                      wanted_course.room,
  //                                      wanted_course);

  if (!pending.pass.room) {

    var busy_rooms = [];
    possible_conflicts.forEach(function (c) {
      if (c.room in rooms.roomgroups) {
        rooms.roomgroups[c.room].forEach(function (r) {
          busy_rooms.push(r);
        });
      }
    });

    var conflict_rooms = [];
    if (wanted_course.room in rooms.roomgroups) {
      rooms.roomgroups[wanted_course.room].forEach(function (r) {
        if (busy_rooms.includes(r)) {
          conflict_rooms.push(r);
        }
      });
    }

    if (conflict_rooms.length > 0) {
      ret.push({
        nok: 'room_busy',
        more: { rooms: [conflict_rooms] }
      });
    }

    extra_unavailable = find_in_pref(extra_pref.rooms, wanted_course.room, wanted_course);

    if (extra_unavailable == 0) {
      ret.push({
        nok: 'room_busy_other_dept',
        more: { room: wanted_course.room }
      });
    }
  }

  return ret;
}


function splash_violated_constraints(check_list, step) {
  var splash_csts;
  var warn_check = warning_check(check_list);
  console.log(warn_check);
  //console.log(pending.wanted_course.id_course);
  if ((logged_usr.rights >> 2) % 2 == 1) {
    var privilege_warning = "Des privilèges vous ont été accordés, et vous en profitez pour outrepasser ";
    if (warn_check.length > 1) {
      privilege_warning += "les contraintes suivantes :";
    } else {
      privilege_warning += "la contrainte suivante :";
    }


    splash_csts = {
      id: "viol_constraint",
      but: {
        list: [{
          txt: "Confirmer",
          click:
            function (btn) {
              pending.pass[btn.pass] = true;
              console.log(pending.wanted_course.id_course);
              check_pending_course();
              return;
            },
          pass: step
        },
        {
          txt: "Annuler",
          click: function (d) {
            pending.rollback();
            go_courses(false);
            return;
          }
        }]
      },
      com: {
        list: [
          { txt: "Attention", ftsi: 23 },
          { txt: "" },
          { txt: privilege_warning }
        ]
      }
    };
    splash_csts.com.list = splash_csts.com.list.concat(warn_check.map(function (el) {
      return { txt: el };
    }));
    splash_csts.com.list.push({ txt: "Confirmer la modification ?" });
  } else {
    /*-- not enough rights, or strong constraints --*/

    var warning_sentence = "Vous tentez d'outrepasser ";
    if (warn_check.length > 1) {
      warning_sentence += "les contraintes suivantes :";
    } else {
      warning_sentence += "la contrainte suivante :";
    }
    splash_csts = {
      id: "viol_constraint",
      but: {
        list: [{
          txt: "Ah ok",
          click: function (d) {
            pending.rollback();
            go_courses(false);
            return;
          }
        }]
      },
      com: {
        list: [{ txt: warning_sentence, ftsi: 23 }
        ]
      }
    };
    splash_csts.com.list = splash_csts.com.list.concat(warn_check.map(function (el) {
      return { txt: el };
    }));
    splash_csts.com.list.push({ txt: "Vous n'avez pas les droits pour le faire..." });
  }
  console.log(splash_csts);
  splash(splash_csts);
}


function clean_pending() {
  // clean pending without waiting for confirmation
  if ((logged_usr.rights >> 2) % 2 != 1) {
    pending.back_init();
    go_courses(false);
  }
}



function check_pending_course() {
  var warn_check = check_course(pending.wanted_course);
  console.log(warn_check);

  if (warn_check.length == 0) {

    add_bouge(pending.init_course);
    //pending.save_wanted() ;
    pending.clean();

    go_grid(true);
    go_courses(true);

  } else { //if (!ngs.dispo) {
    // -- no slot --
    // && (logged_usr.rights >> 2) % 2 == 1) {
    var tutor_constraints = warn_check.filter(function (constraint) {
      return constraint.nok.startsWith("tutor");
    });

    var room_constraints = warn_check.filter(function (constraint) {
      return constraint.nok.startsWith("room");
    });

    var core_constraints = warn_check.filter(function (constraint) {
      return !constraint.nok.startsWith("tutor") && !constraint.nok.startsWith("room");
    });

    if (core_constraints.length > 0) {

      splash_violated_constraints(warn_check, 'core');

      /* TO BE REMOVED
if (slot_case) {
var gs = data_slot_grid.filter(function(s) {
  return s.day == wanted_course.day
    && s.start == wanted_course.start;
});
console.log(gs);
if (gs.length==1) {
  gs[0].pop = true;
}
    } 
      */

    } else if (tutor_constraints.length > 0) {
      if (pending.force.tutor) {
        console.log("tt constraints");
        pending.force.tutor = false;
        compute_cm_room_tutor_direction();
        select_tutor_module_change();
        go_cm_room_tutor_change();
      } else {
        splash_violated_constraints(warn_check, 'tutor');
      }

    } else if (room_constraints.length > 0) {
      if (pending.force.room) {
        pending.force.room = false;
        compute_cm_room_tutor_direction();
        room_cm_level = 0;
        select_room_change();
        go_cm_room_tutor_change();
      } else {
        splash_violated_constraints(warn_check, 'room');
      }
    }

  }

}


function which_slot(x, y, c) {
  var wday = (rootgp_width * labgp.width +
    dim_dispo.plot *
    (dim_dispo.width + dim_dispo.right));
  var iday = Math.floor((x + .5 * cours_width(c)) / wday);
  return {
    day: week_days.day_by_num(iday).ref,
    start_time: indexOf_constraints(c, y) // day-independent
  };
}

// date {day, start_time}
function is_garbage(date) {
  var t = time_settings.time;
  return (date.start_time < t.day_start_time
    || date.start_time >= t.day_finish_time);
}

function is_free(date, promo) {
  return false;
  //    return (promo < 2 && (day == 3 && hour > 2));
}

// find the closest possible start_time in the current day,
// in terms of distance on the screen
function indexOf_constraints(c, y) {
  var course_duration_y = c.duration * nbRows * scale;
  var cst = constraints[c.c_type].allowed_st.map(
    function (d) {
      return {
        y: cours_y({
          start: d,
          promo: c.promo,
        }),
        start: d
      };
    }
  );
  var t = time_settings.time;

  var after = false;
  var i = 0;
  while (!after && i < cst.length) {
    if (cst[i].y > y) {
      after = true;
    } else {
      i++;
    }
  }
  if (i == cst.length) {
    if (y < cst[cst.length - 1].y + course_duration_y) {
      return cst[cst.length - 1].start;
    } else {
      return t.day_finish_time;
    }
  } else if (i == 0) {
    // if (y < 0 - course_duration_y) {
    //     return t.day_start_time - c.duration ;
    // } else {
    return t.day_start_time;
    // }
  } else {
    if (y - cst[i - 1].y > cst[i].y - y) {
      return cst[i].start;
    } else {
      return cst[i - 1].start;
    }
  }
}


/*---------------------
  ------- ROOMS -------
   ---------------------*/

function clean_unavailable_rooms() {
  unavailable_rooms = {};
}


/*--------------------
  ------- TUTORS -----
  --------------------*/


/*---------------------
  ------- VALIDER -----
  ---------------------*/

function create_val_but() {

  edt_but = svg.get_dom("vg")
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
    .attr("y", did.tly);

  edt_but
    .append("text")
    .attr("class", "menu-btn")
    .attr("fill", "white")
    .text("Valider EdT")
    .attr("x", menus.x + menus.mx + .5 * valid.w)
    .attr("y", did.tly + .5 * valid.h);

  edt_but.attr("visibility", "hidden");


  edt_message = svg.get_dom("vg")
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

}




/*--------------------
   ------ STYPE ------
  --------------------*/

function create_stype() {
  var t, dat, datdi, datsmi;

  // -- no slot --
  // --  begin  --
  // TO BE CHECKED: fill missing preferences if needed

  // sometimes, all preferences are not in the database
  // -> by default, not available

  // --   end   --
  // -- no slot --


  dat = svg.get_dom("stg").selectAll(".dispot")
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
    .attr("fill", function (d) {
      return smi_fill(d.value / par_dispos.nmax);
    })
    .attr("width", dispot_w)
    .attr("height", dispot_h)
    .attr("x", dispot_x)
    .attr("y", dispot_y)
    .attr("fill", function (d) {
      return smi_fill(d.value / par_dispos.nmax);
    });

  datdisi
    .append("line")
    .attr("stroke", "#555555")
    .attr("stroke-width", 2)
    .attr("x1", 0)
    .attr("y1", gsclbt_y)
    .attr("x2", gsclbt_x)
    .attr("y2", gsclbt_y);

  svg.get_dom("stg").attr("visibility", "hidden");

  var dis_but = svg.get_dom("stg")
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
    .attr("fill", "white")
    .attr("class", "menu-btn")
    .text("Valider disponibilités")
    .attr("x", did.tlx + .5 * valid.w)
    .attr("y", did.tly + .5 * valid.h);

  var stap_but = svg.get_dom("stg")
    .append("g")
    .attr("but", "st-ap")
    .on("mouseover", st_but_bold)
    .on("mouseout", st_but_back)
    .on("click", apply_stype)
    .attr("cursor", st_but_ptr);

  stap_but
    .append("rect")
    .attr("width", stbut.w)
    .attr("height", stbut.h)
    .attr("x", dispot_but_x)
    .attr("y", dispot_but_y("app"))
    .attr("rx", 10)
    .attr("ry", 10)
    .attr("fill", "steelblue")
    .attr("stroke", "black")
    .attr("stroke-width", 2);

  stap_but
    .append("text")
    .attr("class", "menu-btn")
    .attr("fill", "white")
    .attr("x", dispot_but_txt_x)
    .attr("y", dispot_but_txt_y("app") - 10)
    .text("Appliquer");

  stap_but
    .append("text")
    .attr("class", "menu-btn")
    .attr("fill", "white")
    .attr("x", dispot_but_txt_x)
    .attr("y", dispot_but_txt_y("app") + 10)
    .text("semaine type");

}



function fetch_dispos_type() {
  if (user.name != "") {
    show_loader(true);
    $.ajax({
      type: "GET", //rest Type
      dataType: 'text',
      url: url_fetch_user_dweek + logged_usr.name,
      async: true,
      contentType: "text/csv",
      success: function (msg) {
        //console.log(msg);
        user.dispos_type = [];

        user.dispos_type = d3.csvParse(msg, translate_dispos_type_from_csv);
        create_stype();
        show_loader(false);
      },
      error: function (xhr, error) {
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
  return {
    day: d.day,
    start_time: +d.start_time,
    duration: +d.duration,
    value: +d.value,
    off: -1
  };
}

// -- no slot --
// --  begin  --
// to be extended: intervals could be different
// dt {day, start_time}
function get_dispos_type(dt) {
  var s = user.dispos_type.filter(function (d) {
    return d.day == dt.day && d.start_time == dt.start_time;
  });
  if (s.length != 1) {
    return null;
  } else {
    return s[0];
  }
}
// --   end   --
// -- no slot --




/*--------------------
   ------ ALL ------
   --------------------*/

// function cm_room_launch(d) {
//     if (ckbox["edt-mod"].cked) {
// 	d3.event.preventDefault();
// 	context_menu.room_tutor_hold = true ;
// 	compute_cm_room_tutor_direction();
// 	select_room_change(d);
// 	go_cm_room_tutor_change();
//     }
// }

function select_entry_cm() {
  room_tutor_change.cm_settings = entry_cm_settings;
  var fake_id = new Date();
  fake_id = fake_id.getMilliseconds() + "-" + pending.wanted_course.id_course;
  room_tutor_change.proposal = [{
    fid: fake_id,
    content: "Prof"
  },
  {
    fid: fake_id,
    content: "Salle"
  }];
}




function def_cm_change() {
  entry_cm_settings.click = function (d) {
    context_menu.room_tutor_hold = true;
    if (d.content == 'Salle') {
      // don't consider other constraints than room's
      pending.pass.tutor = true;
      pending.pass.core = true;
      room_cm_level = 0;
      select_room_change();
    } else {
      // don't consider other constraints than tutor's
      pending.pass.room = true;
      pending.pass.core = true;
      select_tutor_module_change();
    }
    go_cm_room_tutor_change();
  };

  tutor_module_cm_settings.click = function (d) {
    context_menu.room_tutor_hold = true;
    if (d.content == '+') {
      select_tutor_filters_change();
    } else {
      confirm_tutor_change(d);
    }
    go_cm_room_tutor_change();
  };

  tutor_filters_cm_settings.click = function (d) {
    context_menu.room_tutor_hold = true;
    select_tutor_change(d);
    go_cm_room_tutor_change();
  };

  tutor_cm_settings.click = function (d) {
    context_menu.room_tutor_hold = true;
    if (d.content == arrow.back) {
      select_tutor_filters_change();
    } else {
      confirm_tutor_change(d);
    }
    go_cm_room_tutor_change();
  };

  for (var level = 0; level < room_cm_settings.length; level++) {
    room_cm_settings[level].click = function (d) {
      context_menu.room_tutor_hold = true;
      if (d.content == '+') {
        room_cm_level += 1;
        select_room_change();
      } else {
        confirm_room_change(d);
      }
      go_cm_room_tutor_change();
    };
  }

  salarie_cm_settings.click = function (d) {
    context_menu.room_tutor_hold = true;
    if (d.content == '+') {
      salarie_cm_level += 1;
      select_salarie_change();
    } else {
      confirm_salarie_change(d);
    }
    go_cm_room_tutor_change();
  };

}


// buttons to open selection view
function create_selections() {

  var avg = svg.get_dom("catg")
    .selectAll(".gen-selection")
    .data(sel_popup.available);

  var contg = avg
    .enter()
    .append("g")
    .attr("class", "gen-selection")
    .attr("transform", sel_trans)
    .attr("cursor", "pointer")
    .on("click", add_panel);

  contg
    .append("rect")
    .attr("width", sel_popup.selw)
    .attr("height", sel_popup.selh)
    .attr("rx", 5)
    .attr("ry", 10)
    .attr("fill", "forestgreen")
    .attr("x", 0)
    .attr("y", 0);

  contg
    .append("text")
    .text(but_open_sel_txt)
    .attr("x", .5 * sel_popup.selw)
    .attr("y", .5 * sel_popup.selh);

  var forall = svg.get_dom("catg")
    .append("g")
    .attr("class", "sel_forall")
    .attr("transform", sel_forall_trans())
    .attr("cursor", "pointer")
    .on("click", apply_cancel_selections);

  forall
    .append("rect")
    .attr("width", .5 * sel_popup.selw)
    .attr("height", sel_popup.selh)
    .attr("class", "select-highlight")
    .attr("rx", 5)
    .attr("ry", 10)
    .attr("x", 0)
    .attr("y", 0);

  forall
    .append("text")
    .text("\u2200")
    .attr("x", .25 * sel_popup.selw)
    .attr("y", .5 * sel_popup.selh);

}

// add data related to a new filter panel if not
// already present
function add_panel(d) {

  var same = sel_popup.panels.find(function (p) {
    return p.type == d.type;
  });

  if (typeof same === 'undefined') {
    var title = "";
    var px = sel_popup.x;
    var py = sel_popup.y;
    var infos = sel_popup.get_available(d.type);
    if (typeof infos !== 'undefined') {
      title = infos.buttxt;
      px = infos.x;
      py = infos.y;
    }
    var panel = {
      type: d.type,
      x: px,
      y: py,
      list: popup_data(d.type),
      txt: title
    };

    sel_popup.panels.push(panel);

    go_selection_popup();

    if (panel.type == "group") {
      go_gp_buttons();
    }
  }
}

// returns the data related to a given filter type
function popup_data(type) {
  switch (type) {
  case "tutor":
    return tutors.all;
  case "module":
    return modules.all;
  case "room":
    return rooms_sel.all;
  default:
    return [];
  }
}


// refreshes filter panels
function go_selection_popup() {

  var bound = svg.get_dom("selg")
    .selectAll(".sel-pop-g")
    .data(sel_popup.panels, function (p) {
      return p.type;
    });


  var g_new = bound
    .enter()
    .append("g")
    .attr("class", "sel-pop-g")
    .attr("id", popup_panel_type_id)
    .call(drag_popup);

  g_new
    .merge(bound)
    .attr("transform", popup_trans);

  var bg_new = g_new
    .append("rect")
    .attr("class", "sel-pop-bg")
    .attr("x", - sel_popup.mar_side)
    .attr("y", - (sel_popup.mar_side + but_exit.side + but_exit.mar_next))
    .attr("width", popup_bg_w);

  bg_new
    .merge(bound.select(".sel-pop-bg"))
    .attr("height", popup_bg_h);

  var exit_new = g_new
    .append("g")
    .attr("class", "sel-pop-exit")
    .attr("cursor", "pointer");

  exit_new
    .merge(bound.select(".sel-pop-exit"))
    .attr("transform", popup_exit_trans)
    .on("click", remove_panel);

  exit_new
    .append("rect")
    .attr("stroke", "none")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", but_exit.side)
    .attr("height", but_exit.side);

  exit_new
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 4)
    .attr("x1", but_exit.mar_side)
    .attr("y1", but_exit.mar_side)
    .attr("x2", but_exit.side - but_exit.mar_side)
    .attr("y2", but_exit.side - but_exit.mar_side);

  exit_new
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 4)
    .attr("x1", but_exit.mar_side)
    .attr("y1", but_exit.side - but_exit.mar_side)
    .attr("x2", but_exit.side - but_exit.mar_side)
    .attr("y2", but_exit.mar_side);


  g_new
    .append("text")
    .text(popup_title_txt)
    .attr("class", "popup-title")
    .attr("x", popup_title_x)
    .attr("y", popup_title_y);


  var contg = g_new
    .filter(function (p) {
      return p.type != "group";
    })
    .append("g")
    .attr("class", "sel-pop-all")
    .attr("cursor", "pointer")
    .on("click", apply_selection_display_all);

  contg
    .append("rect")
    .attr("width", popup_all_w)
    .attr("height", popup_all_h)
    .attr("class", "select-highlight")
    .attr("rx", 5)
    .attr("ry", 10)
    .attr("x", 0)
    .attr("y", 0);

  contg
    .append("text")
    .text("\u2200")
    .attr("x", popup_all_txt_x)
    .attr("y", popup_all_txt_y);

  bound.exit().remove();

  go_selection_buttons();

}


// create buttons for department redirection
function create_dept_redirection() {
  var avg = svg.get_dom("catg")
    .selectAll(".dept-selection")
    .data(departments.data);

  var contg = avg
    .enter()
    .append("g")
    .attr("class", "dept-selection")
    .attr("transform", depts_trans)
    .attr("cursor", "pointer")
    .on("click", redirect_dept);

  contg
    .append("rect")
    .attr("class", "select-highlight")
    .attr("width", departments.w)
    .attr("height", departments.h)
    .attr("rx", 5)
    .attr("ry", 10)
    .attr("fill", "forestgreen")
    .attr("x", 0)
    .attr("y", 0);

  contg
    .append("text")
    .text(dept_txt)
    .attr("x", .5 * departments.w)
    .attr("y", .5 * departments.h);
}
