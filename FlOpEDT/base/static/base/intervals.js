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
    var t = time_settings.time ;
    
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
    
    var i_start = index_in_pref(pref, start_time) ;
    var i_end = index_in_pref(pref, start_time+duration) ;
    var i, tot_weight, start_inter, end_inter ;
    var average_pref = 0 ;
    var unknown = false ;
    var unavailable = false ;

    if (i_start==0 || i_start==pref.length || i_end==0 || i_end==pref.length){
	return -1 ;
    }

    i = i_start - 1 ;
    while (!unknown && !unavailable && i < i_end) {
	if(i==i_start - 1) {
	    start_inter = start_time ;
	} else {
	    start_inter = pref.start_time ;
	}
	if(i==i_end - 1) {
	    end_inter = start_time + duration ;
	} else {
	    end_inter = pref.start_time + pref.duration ;
	}
	average_pref += (end_inter-start_inter) * pref.value ;
	tot_weight += end_inter-start_inter ;
	unknown = (pref.value == -1) ;
	unavailable = (pref.value == 0) ;
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
    var i_start = index_in_pref(list, start_time) ;
    var i_end = index_in_pref(list, start_time+duration) ;

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
