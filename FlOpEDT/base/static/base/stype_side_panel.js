var tutor_list = [] ;

// open side panel
function openNav() {

    is_side_panel_open = true ;

    // open panel
    document.getElementById("side_panel").style.width = "250px";
    document.getElementById("content").style.marginLeft = "250px";
    document.getElementById("menu-edt").style.marginLeft = "250px";

    $('#sp_tutor').hide();
    $('#sp_course_type').hide();

    // add event listener
    $('#dd_tutors').on('change', function (e) {
        user.nom = this.value;
        fetch_pref_only();
    });

    // fetch the copy numbers
    fetch_tutor_list();
}


// close the side panel
function closeNav() {
    // avoid fetching work copy numbers if closed
    is_side_panel_open = false ;

    // close panel
    document.getElementById("side_panel").style.width = "0";
    document.getElementById("content").style.marginLeft= "0";
    document.getElementById("menu-edt").style.marginLeft= "0";
}

// fetch tutors whose main department is the current department,
// and fill the dropdown list
function fetch_tutor_list(){
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: url_all_tutors,
        async: true,
        contentType: "application/json; charset=utf-8",
        success: function(msg) {
            console.log(msg);
            // add tutors
            var tutors = msg.tutors ;
            tutors.sort() ;
            var option ;
            for (var i=0 ; i<tutors.length ; i++){
                option = {value:tutors[i], text:tutors[i]} ;
                $('#dd_tutors').append($('<option>', option));
            }
        },
        error: function(msg) {
            console.log("error");
        }
    });
};

// show tutor selection in the side panel
function show_tutors() {
    $('#sp_course_type').hide();
    $('#sp_tutor').show();

    
}

// show course type selection in the side panel
function show_course_types(){
    $('#sp_tutor').hide();
    $('#sp_course_type').show();
}
