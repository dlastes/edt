// drop down list parameters
dd_selections['tutor'].url = url_all_tutors ;
dd_selections['tutor'].id ="#dd_tutors";
dd_selections['type'].url = url_course_types ;
dd_selections['type'].id ="#dd_course_types";
dd_selections['prog'].url = url_training_programmes;
dd_selections['prog'].id = "#dd_programmes" ;

for (var key in dd_selections){
    dd_selections[key].filled = false ;
}


// fetch data and fill the dropdown list
function fetch_infos_dd(dd){
    if (!dd.filled) {
        console.log(dd.url);        
        $.ajax({
            type: "GET",
            dataType: 'json',
            url: dd.url,
            async: true,
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                // add elements in the dropdown list
                data.sort() ;
                var option ;
                for (var i=0 ; i<data.length ; i++){
                    option = {value:data[i], text:data[i]} ;
                    $(dd.id).append($('<option>', option));
                }
                dd.filled = true ;
                dd_fetch_ended() ;
            },
            error: function(msg) {
                console.log("error");
            }
        });
    }
};



// read selected values in dd lists and fetch corresponding data
function fetch_selected() {
    for(var key in dd_selections) {
        dd_selections[key].value = $(dd_selections[key].id).find(':selected').val() ;
    }
    if (mode == 'tutor') {
        user.name = dd_selections['tutor'].value;
    } else {
        user.name = course_type_prog_name(
            dd_selections['prog'].value,
            dd_selections['type'].value) ;
    }
    fetch_pref_only();
}


// save the default values of the dd lists when filled
function dd_fetch_ended() {
    if (mode == 'tutor' && dd_selections['tutor'].filled) {
        // select logged user if present
        var me = $(dd_selections['tutor'].id + " option[value='" + logged_usr.name + "']");
        if (typeof me !== 'undefined') {
            me.prop('selected', true);
        }
        fetch_selected();
    } else if (mode == 'course' && dd_selections['type'].filled && dd_selections['prog'].filled) {
        fetch_selected();
    }
}

// open side panel
function openNav() {

    is_side_panel_open = true ;

    // open panel
    $("#side_panel").show();
    document.getElementById("side_panel").style.width = "250px";
    document.getElementById("content").style.marginLeft = "250px";
    document.getElementById("menu-edt").style.marginLeft = "250px";

//    $('#sp_tutor').hide();
    $('#sp_course_type').hide();

    // add event listeners
    for (var key in dd_selections) {
        $(dd_selections[key].id).on('change', function (e) {
            fetch_selected();
        });
    }
    

    // fetch the tutors, course types and training programmes
    for (var key in dd_selections) {
        fetch_infos_dd(dd_selections[key]);
    }
}


// close the side panel
function closeNav() {
    // avoid fetching work copy numbers if closed
    is_side_panel_open = false ;

    // close panel
    $("#side_panel").hide();
    document.getElementById("side_panel").style.width = "0";
    document.getElementById("content").style.marginLeft= "0";
    document.getElementById("menu-edt").style.marginLeft= "0";
}


// show tutor selection in the side panel
function show_tutors() {
    // refresh side panel
    $('#sp_course_type').hide();
    $('#sp_tutor').show();

    // change button behaviors
    mode = "tutor" ;

    fetch_selected();
}



// show course type selection in the side panel
function show_course_types(){
    $('#sp_tutor').hide();
    $('#sp_course_type').show();

    // change button behaviors
    mode = "course" ;

    fetch_selected();
}
