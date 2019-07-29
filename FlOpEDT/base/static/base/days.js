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

function Day(day={num:iday,
                  date:"01/01",
                  ref:"m",
                  name:"Lun."}) {
    this.num = day.num ;
    this.date = day.date ;
    this.ref = day.ref ;
    this.name = day.name ;
}

// 'static' function 
Day.id_fun = function(d) {
    return d.date;
}



function WeekDays(days = []) {
    this.day_list = [] ;
    this.day_dict = {} ;
    days.forEach(function(day) {
        this.add_day(day);
    }, this);
}

WeekDays.prototype.nb_days = function() {
    return this.day_list.length ;
}

WeekDays.prototype.day_by_ref = function(ref) {
    return this.day_dict[ref] ;
}

WeekDays.prototype.day_by_num = function(num) {
    return this.day_list.find(function(d) {
        return d.num == num ;
    });
}

WeekDays.prototype.data = function() {
    return this.day_list ;
}

WeekDays.prototype.refs = function() {
    return Object.keys(this.day_list) ;
}

WeekDays.prototype.forEach = function(callback, this_arg) {
    return this.day_list.forEach(callback, this_arg) ;
}

WeekDays.prototype.add_day = function(day={num:iday,
                                           date:"01/01",
                                           ref:"m",
                                           name:"Lun."}) {
    var new_day = new Day(day) ;
    this.day_list.push(new_day);
    this.day_dict[new_day.ref] = new_day ;
}

