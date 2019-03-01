function openNav() {
  document.getElementById("mySidebar").style.width = "250px";
  document.getElementById("edt-main").style.marginLeft = "250px";
  document.getElementById("menu-edt").style.marginLeft = "250px";
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
        },
        error: function(msg) {
            console.log("error");
        }
    });

}

function sendForm(){

}