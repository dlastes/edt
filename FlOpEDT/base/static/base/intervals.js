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
//        list.length if instant>list[j]
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
function get_preference(day, start_time, duration, tutor) {
    var after = false ;
    var pref = dispos[tutor][day];
    var t = time_settings.time ;
    
    var i_start = index_in_pref(pref.map(function(d){return d.start_time;}), start_time) ;
    var i_end = index_in_pref(pref.map(function(d){return d.start_time;}), start_time+duration) ;

    var i, tot_weight, start_inter, end_inter, w ;
    var average_pref = 0 ;
    var unknown = false ;
    var unavailable = false ;

    if (i_start==0 || i_start==pref.length || i_end==0 || i_end==pref.length){
	return -1 ;
    }

    i = i_start - 1 ;
    tot_weight = 0 ;
    while (!unknown && !unavailable && i < i_end) {
	if(i==i_start - 1) {
	    start_inter = start_time ;
	} else {
	    start_inter = pref[i].start_time ;
	}
	if(i==i_end - 1) {
	    end_inter = start_time + duration ;
	} else {
	    end_inter = pref[i].start_time + pref[i].duration ;
	}
	w = (end_inter-start_inter) ;
	average_pref += w * pref[i].value ;
	tot_weight += w ;
	unknown = (pref[i].value == -1 && w>0) ;
	unavailable = (pref[i].value == 0 && w>0) ;
	i++;
    }
    if (unavailable) {
	return 0 ;
    }
    if (unknown) {
	return -1 ;
    }
    
    return average_pref/tot_weight ;
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
    var pref = dispos[user.nom][day];
    var p = pref.filter(function(d) {
	return d.start_time == start_time;
    });
    if (p.length == 1) {
	p[0].val = value ;
    } else {
	console.log("Problem with the time interval");
    }
    if (user.nom == tutor) {
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

