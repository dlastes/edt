// Text for morning preferences
// Text for preferences concerning day length
// Text for hole preferences, if you want or not between courses
// Text for preferences concerning if you want to eat early or late
function txt_morning_half(val, id) {
  if (id == 'morning') {
    switch (val) {
    case "0":
        return 'Commencer le plus tôt possible mais finir tôt';
        break;
    case "0.25":
        return 'Ne pas commencer trop tard et ne pas finir trop tard';
        break;
    case "0.5":
        return 'Ni trop tôt ni trop tard';
        break;
    case "0.75":
        return 'Ne pas commencer trop tôt et finir plus tard';
        break;
    case "1":
        return 'Commencer le plus tard possible mais finir tard';
        break;
    }
  } 
  if (id == 'free_half_day'){
    switch (val) {
    case "0":
        return 'Avoir toute la semaine des journées allégées';
        break;
    case "0.25":
        return 'Avoir plus de journées allégées que de demi-journées libérées';
        break;
    case "0.5":
        return 'Avoir des semaines équilibrées';
        break;
    case "0.75":
        return 'Avoir plus de demi-journées libérées que de journées allégées';
        break;
    case "1":
        return 'Avoir des journées chargées mais aussi des demi-journées libérées';
        break;
    }
  }
  if (id == 'hole'){
    switch (val) {
    case "0":
        return 'Ne pas avoir de trous entre deux cours';
        break;
    case "0.5":
        return 'Indifférent';
        break;
    case "1":
        return 'Avoir des trous entre deux cours';
        break;
    }
  }
  if (id == 'selfeat'){
    switch (val) {
    case "0":
        return 'Manger plus tôt';
        break;
    case "0.5":
        return 'Indifférent';
        break;
    case "1":
        return 'Manger plus tard';
        break;
    }
  }
}


// update comments associated with range value
function update_comment(id) {
  return function () {
    var txt = txt_morning_half($('#'+id).val(), id);
        $('#'+id).next().text(txt);
    } ;
}

// main
$(function() {
    var ids = ['morning', 'free_half_day', 'hole', 'selfeat'] ;
    ids.forEach(function(id) {
        $('#'+id).on('input', update_comment(id));
        $(document).ready(update_comment(id));
    });
});



//Creation of the little board
let len_square = 180;
let x=180;
let id=0;

for (var i = 0; i < 5; i++) {
 
    d3.select("svg#grille")
    .append("rect")
    .attr("id", id+1)
    .attr("fill", "green" )
    .attr("width", 110)
    .attr("height", 95)
    .attr("x", x)
    .attr("y", 10);

     d3.select("svg#grille")
    .append("rect")
    .attr("id", id+2)
    .attr("fill", "green")
    .attr("width", 110)
    .attr("height", 95)
    .attr("x", x)
    .attr("y", 105);
    

    id += 2;
    x += 110;
}


for (var i = 0; i < 6; i++) {
 

    d3.select("svg#grille")
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .attr("x1", len_square*1)
    .attr("y1", 10)
    .attr("x2", len_square*1)
    .attr("y2", 200);

    len_square +=  110;

}

let line = 10;

for (var j = 0; j < 3; j++) {

    d3.select("svg#grille")
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .attr("x1", 180)
    .attr("y1", line)
    .attr("x2", 730)
    .attr("y2", line);


    line +=  95;
}

let tableau = new Object();
tableau.color = [{"name":"vert","color":"green"},
                {"name":"rouge","color":"red"}];

tableau.cells = [{"x":0,"y":0, "p":"vert"},
              {"x":0,"y":1, "p":"vert"},
              {"x":0,"y":2, "p":"vert"},
              {"x":0,"y":3, "p":"vert"},
              {"x":0,"y":4, "p":"vert"},
              {"x":1,"y":0, "p":"vert"},
              {"x":1,"y":1, "p":"vert"},
              {"x":1,"y":2, "p":"vert"},
              {"x":1,"y":3, "p":"vert"},
              {"x":1,"y":4, "p":"vert"}
             ];

// create a Map to store color informations
let color = new Map();
let turns = new Array();

for (var z=0; z<tableau.color.length; z++ ) {
  color.set( tableau.color[z].name , tableau.color[z] );
  turns[z] = tableau.color[z].name;
}
turns[z] = "n";

// returns the center x coordinate
function move_x(m) {
    return m.x * len_square + len_square/2 ;
}
// returns the center y coordinate
function move_y(m) {
    return m.y * len_square + len_square/2 ;
}

// returns the color used
function move_color(m) {
  let colorName = m.p;
  if ( color.has(colorName) ) {
    return color.get(colorName).color;
  } /*else {
    return defaultColor;
  }*/
}
// propose another color for this move
function move_click(m) {
    let actual_color = turns.indexOf(m.p);
    m.p = turns[ (actual_color+1) % turns.length ];
    display_move() ;
   }

function display_move() {
  let moves = 
  d3.select("svg#grille")
    .selectAll("rect")
    .data(tableau.cells);

  let new_moves = moves
    .enter()
    .append("rect")
    .attr("cx", move_x)
    .attr("cy", move_y)
    .on("click",move_click);

  new_moves
    .merge(moves)
    .attr("fill", move_color);

}
display_move();
