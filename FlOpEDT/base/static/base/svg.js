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


// "svg" will be the svg container
function Svg(light) {
    this.layout = {} ;
    this.layout["svg"] = null ;
    this.light = light ;
}

// {parent:, name:, children: }
// name -> 

Svg.prototype.add_child = function(parent_name, child_name) {
    if (Object.keys(this.layout).includes(child_name)) {
        console.log("Name " + child_name + " already in use");
        return null;
    }
    if (!Object.keys(this.layout).includes(parent_name)) {
        console.log("Parent "+ parent_name + " unknown");
        return null;
    }
    this.layout[child_name] = this.layout[parent_name]
        .append("g").attr("id","layout-" + child_name) ;
    return this.layout[child_name] ;
}

Svg.prototype.get_dom = function(name) {
    return this.layout[name] ;
}

Svg.prototype.create_container = function() {
    var tot;

    if (this.light) {
        tot = d3.select("body");
    } else {
        tot = d3.select("body").append("div");
    }

    this.layout["svg"] = tot
        .append("svg")
        .attr("width", dsp_svg.w)
        .attr("height", dsp_svg.h)
        .attr("id", "edt-main")
        .append("g")
        .attr("transform", dsp_svg.trans());

    this.create_layouts();
}

Svg.prototype.create_layouts = function() {
    // menus ground
    this.add_child("svg", "meg");

    // weeks ground
    this.add_child("svg", "wg");
    this.add_child("wg", "wg-bg");
    this.add_child("wg", "wg-fg");

    // groupes ground
    // gpg = this.add_child("svg", "gpg");

    // selection categories button ground
    this.add_child("svg", "catg");

    // semaine type ground
    this.add_child("svg", "stg");

    // dispos info ground
    this.add_child("svg", "dig");

    // valider
    this.add_child("svg", "vg");

    // background, middleground, foreground, dragground
    this.add_child("svg", "edtg");
    this.add_child("edtg", "edt-bg");
    this.add_child("edtg", "edt-mg");
    this.add_child("edtg", "edt-fig");
    this.add_child("edtg", "edt-fg");

    // selection ground
    this.add_child("svg", "selg");

    
    // context menus ground
    this.add_child("svg", "cmg");
    this.add_child("cmg", "cmpg");
    this.add_child("cmg", "cmtg");
    

    // logo ground
    // log = this.add_child("edtg", "log");

    // drag ground
    this.add_child("svg", "dg");

    this.get_dom("edt-bg")
	.append("rect")
	.attr("class","rbg");
}
