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

class Day {
    constructor(day={num:iday,
                     date:"01/01",
                     ref:"m",
                     name:"Lun."}) {
        this.num = day.num ;
        this.date = day.date ;
        this.ref = day.ref ;
        this.name = day.name ;
    }

    static id_fun() {
        return function(d) {
    	    return d.date;
        } ; 
    }
}


class WeekDays {
    // days: list of Day
    constructor(days = []) {
        this.day_list = [] ;
        this.day_dict = {} ;
        days.forEach(function(day) {
            this.add_day(day);
        }, this);
    }

    get nb_days() {
        return this.day_list.length ;
    }

    day_by_ref(ref) {
        return this.day_dict[ref] ;
    }

    day_by_num(num) {
        return this.day_list.find(function(d) {
            return d.num == num ;
        });
    }

    get data() {
        return this.day_list ;
    }

    get refs() {
        return Object.keys(this.day_list) ;
    }

    forEach(callback, this_arg) {
        return this.day_list.forEach(callback, this_arg) ;
    }

    add_day(day={num:iday,
                 date:"01/01",
                 ref:"m",
                 name:"Lun."}) {
        var new_day = new Day(day) ;
        this.day_list.push(new_day);
        this.day_dict[new_day.ref] = new_day ;
    }

    
}
