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



/*
    Display the number of days of inactivity for each room
*/
function displayRoomActivity(data){
    rooms = d3.select('#statistics')
        .data(data.room_activity)
        .enter()
        .append('div')

    // Room name
    rooms
        .append('div')
        .text((d)=> d.room)

    // Number of days of inactivity
    rooms
        .append('div')
        .text((d)=> d.count)        
}

/*
    Global method to request statistics 
*/
function fetchStatistcs(url, callback) {
    $.ajax({
        type: "GET",
        dataType: 'text',
        url: url,
        async: true,
        contentType: "text/json",
        success: function (value) {
            data = JSON.parse(value)
            callback(data);
        },
        error: function (xhr, error) {
            console.log(xhr);
            console.log(error);
        }
    });
}

document.addEventListener('DOMContentLoaded', () => fetchStatistcs(url_room_activity, displayRoomActivity));
