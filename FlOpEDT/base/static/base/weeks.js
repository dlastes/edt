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


/**************/
/* class Week */
/**************/

function Week (an, semaine) {
    this.an = an ;
    this.semaine = semaine ;
}

// useful for url generation
Week.prototype.url = function() {
    return this.an + "/" + this.semaine ;
}

// comparison function
Week.compare = function(week_a, week_b){
    if(week_a.an < week_b.an) {
        return -1 ;
    }
    if (week_a.an == week_b.an) {
        if (week_a.semaine < week_b.semaine) {
            return -1 ;
        } else if (week_a.semaine == week_b.semaine) {
            return 0 ;
        }
    }
    return 1 ;
}

// id function
Week.id_fun = function(week) {
    return "Y" + week.an + "-W" + week.semaine ;
}




/**********************/
/* class WeeksExcerpt */
/**********************/
// desired_nb: target size of the excerpt
// full_weeks: list of weeks forming the full set
// nb: actual size of the excerpt
// first: index in the full list of the first element of the excerpt
// selected: index in the full list of the selected element
// data: list of weeks of the excerpt


function WeeksExcerpt(desired_nb) {
    this.desired_nb = desired_nb ;
    this.full_weeks = new Weeks() ;
    // first and selected undefined until full_weeks is not empty
}

// add weeks to full_weeks
WeeksExcerpt.prototype.add_full_weeks = function(weeks) {
    this.full_weeks.add_all(weeks) ;
    this.adapt_full_weeks() ;
    this.first = 0 ;
    this.selected = 0 ;
}
// the excerpt should not exceed full weeks size
WeeksExcerpt.prototype.adapt_full_weeks = function() {
    this.nb = Math.min(this.desired_nb, this.full_weeks.get_nb()) ;
}

// getter for the selected index
WeeksExcerpt.prototype.get_iselected = function() {
    return [this.selected] ;
}
// getter for the selected week
WeeksExcerpt.prototype.get_selected = function() {
    return this.full_weeks.data[this.selected] ;
}


// try to go at week chosen, and set the window around
// week: Week
WeeksExcerpt.prototype.chose = function(chosen) {
    var min = this.full_weeks.get_min() ;
    var max = this.full_weeks.get_max() ;

    if (Week.compare(min, chosen) < 0) {
        // pick the first week
        this.first = 0 ;
        this.selected = 0 ;
    } else if (Week.compare(chosen, max) > 0) {
        // pick the last week
        this.first = this.full_weeks.get_nb() - this.nb ;
        this.selected = this.full_weeks.get_nb() - 1 ;
    } else {
        // pick the first not greater than chosen week
        var not_less = this.full_weeks.data.find(function(week){
            return Week.compare(week, chosen) >= 0 ;
        });
        this.selected = this.full_weeks.data.indexOf(not_less);
        this.first = Math.min(this.selected, this.full_weeks.get_nb() - this.nb);
    }
    // extract the data
    this.data = this.full_weeks.data.slice(this.first,
                                           this.first + this.nb);
}

// move the excerpt data to earlier weeks
WeeksExcerpt.prototype.move_earlier = function() {
    if (this.first > 0) {
        this.first -= 1;
        this.data.pop();
        this.data.unshift(this.full_weeks.data[this.first]);
    }
}

// move the excerpt data to later weeks
WeeksExcerpt.prototype.move_later = function() {
    if (this.first + this.nb < this.full_weeks.get_nb()) {
        this.first += 1;
        this.data.splice(0, 1);
        this.data.push(this.full_weeks.data[this.first + this.nb]);
    }
}

// new selection
WeeksExcerpt.prototype.change_selection = function(shift) {
    if (shift >= 0 && shift < this.nb) {
        this.selected = this.first + shift ;
    }
}






/***************/
/* class Weeks */
/***************/
// data: list of Week; all weeks of the school year

// all_weeks: list of {semaine:,an:}
function Weeks(all_weeks) {
    if(typeof all_weeks === 'undefined') {
        all_weeks = [] ;
    }
    this.data = [] ;
    this.add_all(all_weeks) ;
    this.data.sort(Week.compare) ;
}

Weeks.prototype.add_all = function(all_weeks){
    all_weeks.forEach(function(week) {
        this.data.push(new Week(week.an, week.semaine)) ;
    }, this) ;
}


Weeks.prototype.get_min = function(){
    return this.data[0];
}

Weeks.prototype.get_max = function(){
    return this.data[this.data.length - 1];
}

Weeks.prototype.get_nb = function() {
    return this.data.length ;
}


