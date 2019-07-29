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


