function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("edt-main").style.marginLeft = "250px";
    document.getElementById("menu-edt").style.marginLeft = "250px";

    var cur_week = weeks.init_data[weeks.sel[0]].semaine;
    var cur_year = weeks.init_data[weeks.sel[0]].an;

    $.ajax({
        type: "GET",
        dataType: 'text',
        url: url_side_pannel +  cur_year + '/' + cur_week,
        async: true,
        contentType: "text/html",
        success: function(msg, ts, req) {
            console.log(msg);
            document.getElementById('mySidebar').innerHTML = msg ;
        },
        error: function(msg) {
            console.log("error");
        }
    });
    
}

function closeNav() {
  document.getElementById("mySidebar").style.width = "0";
  document.getElementById("edt-main").style.marginLeft= "0";
  document.getElementById("menu-edt").style.marginLeft= "0";
}

function getForm( funcname ) {
	
	$.ajax({
        type: "GET",
        dataType: 'text',
        url: "ttapp/viewForm/" + funcname,
        async: true,
        contentType: "text/html",
        success: function(msg, ts, req) {
            console.log( msg );
            document.getElementById('sideBarForm').innerHTML = msg;
        },
        error: function(msg) {
            console.log("error");
        }
    });

}