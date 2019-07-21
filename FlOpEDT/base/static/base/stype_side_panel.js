var tutor_list = [] ;

var dds = {tutor:{url: url_all_tutors, id:"dd_tutors"},
           type:{url: url_course_types, id:"dd_course_types"},
           prog:{url: url_training_programmes, id:"dd_programmes"}};


// fetch tutors whose main department is the current department,
// and fill the dropdown list
function fetch_infos_dd(dd){
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: dd.url,
        async: true,
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            // add tutors in the dropdown list
            data.sort() ;
            var option ;
            for (var i=0 ; i<data.length ; i++){
                option = {value:data[i], text:data[i]} ;
                $('#'+dd.id).append($('<option>', option));
            }
        },
        error: function(msg) {
            console.log("error");
        }
    });
};


// open side panel
function openNav() {

    is_side_panel_open = true ;

    // open panel
    document.getElementById("side_panel").style.width = "250px";
    document.getElementById("content").style.marginLeft = "250px";
    document.getElementById("menu-edt").style.marginLeft = "250px";

    $('#sp_tutor').hide();
    $('#sp_course_type').hide();

    // add event listeners
    $('#'+dds.tutor.id).on('change', function (e) {
        user.nom = this.value;
        fetch_pref_only();
    });

    // fetch the tutors, course types and training programmes
    fetch_infos_dd(dds.tutor);
    fetch_infos_dd(dds.type);
    fetch_infos_dd(dds.prog);
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
