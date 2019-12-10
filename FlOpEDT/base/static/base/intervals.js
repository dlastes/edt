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


// list: list of time interval
// instant: moment in time
// return the index i such that list[i-1]<=instant<list[i] if exists
//        0 if instant<list[0]
//        list.length if instant>=list[j]
function index_in_pref(list, instant) {
    var after = false ;
    var i = 0 ;

    while(! after && i < list.length) {
	if (list[i] > instant) {
	    after = true ;
	} else {
	    i ++ ;
	}
    }
    return i ;
}




// get the aggregated preference score of tutor on day, on an interval
// lasting duration, starting at start_time
// assumes well-formed (consecutive) intervals
function get_preference(pref, start_time, duration) {
    var after = false ;
    var t = time_settings.time ;

    
    if (pref.length == 0) {
        return -1 ;
    }

    var instants = pref.map(function(d){
        return d.start_time;
    });
    instants.push(pref[pref.length-1].start_time);

    var i_start = index_in_pref(instants, start_time);
    var i_end = index_in_pref(instants, start_time + duration);
    if(i_end > 0 && instants[i_end-1] == start_time + duration) {
        i_end -= 1 ;
    }
    
    var unavailable, unknown ;

    unknown = false ;
    if  (i_start == 0 || i_end == instants.length) {
        if (i_start == i_end) {
            return -1 ;
        } else {
            unknown = true ;
        }
    }

    i_start = Math.max(0, i_start) ;
    i_end = Math.min(pref.length - 1, i_end) ; //
    var i, tot_weight, weighted_pref, w ;
    var weighted_pref = 0 ;
    var tot_weight = 0 ;

    unavailable = false ;
    i = i_start ;
    while (i <= i_end && !unavailable) {
        if (pref[i].value == 0) {
            unavailable = true ;
        } else {
            w = pref[i].duration
                - Math.max(0, start_time-pref[i].start_time)
                - Math.max(0, start_time + duration -
                           (pref[i].start_time + pref[i].duration));
            tot_weight += w ;
            weighted_pref += w * pref[i].value ;
        }
        i += 1 ;
    }

    if (unavailable) {
	return 0 ;
    }
    if (unknown) {
	return -1 ;
    }

    
    
    return weighted_pref/tot_weight ;
}


// period: {day: , start:, duration: }
function find_in_pref(pref, entity, period) {
    if (!Object.keys(pref).includes(entity)) {
        return undefined ;
    }
    if (!Object.keys(pref[entity]).includes(period.day)) {
        return undefined ;
    }
    
    return get_preference(pref[entity][period.day],
                          period.start, period.duration);
}



function no_overlap(list, start_time, duration) {
    var i_start = index_in_pref(list.map(function(d){return d.start_time;}), start_time) ;
    var i_end = index_in_pref(list.map(function(d){return d.start_time;}), start_time+duration) ;

    if (i_start != i_end) {
	return false ;
    }
    if (i_start==0 || i_start==list.length) {
	return true ;
    }
    if (list[i_start-1].start_time + list[i_start-1].duration
	<= start_time
	&& start_time+duration <= list[i_end].start_time) {
	return true ;
    }
    return false ;
}



function update_pref_interval(tutor, day, start_time, value) {
    var pref = dispos[user.name][day];
    var p = pref.filter(function(d) {
	return d.start_time == start_time;
    });
    if (p.length == 1) {
	p[0].value = value ;
    } else {
	console.log("Problem with the time interval");
    }
    if (user.name == tutor) {
	pref = user.dispos ;
	p = pref.filter(function(d) {
	    return d.day == day && d.start_time == start_time;
	});
	console.log(p);
	if (p.length == 1) {
	    p[0].val = value ;
	} else {
	    console.log("Problem with the time interval");
	}
    }
}


// PRECOND: sorted preference list
// fill preference list with def_value so that any moment has a value
function fill_holes(pref, def_value) {
    var i = 0 ;
    while (i < pref.length-1) {
        if (pref[i].start_time + pref[i].duration < pref[i+1].start_time) {
            pref.splice(i+1, 0,
                        {start_time:pref[i].start_time + pref[i].duration,
                         duration: pref[i+1].start_time - pref[i].duration,
                         value: def_value});
            i++;
        }
        i ++ ;
    }
}
