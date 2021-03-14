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
        return 'Indifférent';
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
        return 'Indifférent';
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

let grille = d3.select("svg#grille");

//Creation of the little board
let len_square = 95;
let id=0;
let y_start = 5;
let x_start = 5;

for (var i = 0; i < 5; i++) {
 
    grille
    .append("rect")
    .attr("id", id+1)
    .attr("fill", "green" )
    .attr("width", len_square)
    .attr("height", len_square)
    .attr("x", x_start + i*len_square)
    .attr("y", y_start);

     d3.select("svg#grille")
    .append("rect")
    .attr("id", id+2)
    .attr("fill", "green")
    .attr("width", len_square)
    .attr("height", len_square)
    .attr("x", x_start + i*len_square)
    .attr("y", y_start + len_square);
    id += 2;
}


for (let i = 0; i < 6; i++) {
    d3.select("svg#grille")
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .attr("x1", x_start + i * len_square)
    .attr("y1", y_start)
    .attr("x2", x_start + i * len_square)
    .attr("y2", y_start + 2 * len_square);
}


for (let i = 0; i < 3; i++) {
    d3.select("svg#grille")
    .append("line")
    .attr("stroke", "black")
    .attr("stroke-width", 2)
    .attr("x1", x_start)
    .attr("y1", y_start + i * len_square)
    .attr("x2", x_start + 5 * len_square)
    .attr("y2", y_start + i * len_square);
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
