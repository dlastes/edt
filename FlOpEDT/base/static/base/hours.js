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


function Hours(settings) {
  // side time scale: list of {h: int, hd:('am'|'pm')}
  this.data = [];
  var stime = Math.floor(settings.day_start_time / 60);
  if (stime * 60 < settings.day_start_time) {
    stime++;
  }
  while (stime * 60 <= settings.day_finish_time) {
    if (stime * 60 <= settings.lunch_break_start_time) {
      this.data.push({ h: stime, hd: 'am' });
    }
    if (stime * 60 >= settings.lunch_break_finish_time) {
      this.data.push({ h: stime, hd: 'pm' });
    }
    stime++;
  }
  this.settings = settings;
}


// Hour labels to the left of the grid
function HourHeader(svg, layout_name, hours) {
  this.layout = svg.get_dom(layout_name);
  this.hours = hours;
  this.mix = new HourMix(this.hours.settings);
  hard_bind(this.mix);
}

HourHeader.prototype.update = function (quick) {

  var t = get_transition(quick);

  var hour_bar = this.layout
    .selectAll(".gridsckhb")
    .data([time_settings.time]);

  var hourbar_g = hour_bar
    .enter()
    .append("g")
    .attr("class", "gridsckhb");

  hourbar_g
    .append("line")
    .attr("class", "gridsckhlam")
    .merge(hour_bar.select(".gridsckhlam"))
    .transition(t)
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", 0)
    .attr("y2", bknews_top_y());

  hourbar_g
    .append("line")
    .attr("class", "gridsckhlpm")
    .merge(hour_bar.select(".gridsckhlpm"))
    .transition(t)
    .attr("x1", 0)
    .attr("y1", bknews_bot_y())
    .attr("x2", 0)
    .attr("y2", grid_height());

  hour_bar.exit().remove();

  var hour_scale = svg.get_dom("edt-fg")
    .selectAll(".gridsckh")
    .data(this.hours.data);

  var hour_sc_g = hour_scale
    .enter()
    .append("g")
    .attr("class", "gridsckh");

  hour_sc_g
    .append("line")
    .attr("class", "gridsckhl")
    .merge(hour_scale.select(".gridsckhl"))
    .transition(t)
    .attr("x1", this.mix.gsckh_x1)
    .attr("y1", this.mix.gsckh_y)
    .attr("x2", this.mix.gsckh_x2)
    .attr("y2", this.mix.gsckh_y);

  hour_sc_g
    .append("text")
    .merge(hour_scale.select("text"))
    .transition(t)
    .text(this.mix.gsckh_txt)
    .attr("x", this.mix.gsckh_x2() - 2)
    .attr("y", this.mix.gsckh_y);


  hour_scale.exit().remove();

};


// Display parameters and functions
function HourMix(settings) {
  this.settings = settings;
  this.gsckh_x1 = function () {
    return 0;
  };
  this.gsckh_x2 = function () {
    return -5;
  };
  this.gsckh_y = function (d) {
    var ret = (d.h * 60 - this.settings.day_start_time) * nbRows * scale;
    if (d.hd == 'pm') {
      ret += bknews_h()
        - (this.settings.lunch_break_finish_time
          - this.settings.lunch_break_start_time) * nbRows * scale;
    }
    return ret;
  };
  this.gsckh_txt = function (d) {
    var ret = d.h;
    if (ret >= 24) {
      ret -= 24;
    }
    ret += "h";
    return ret;
  };
}
