
function send_form(form) {
    $("#"+form).submit(function(event){
        event.preventDefault();
        let post_url = $(this).attr("action");
        let request_method = $(this).attr("method");
        let data = new FormData($("#"+form).get(0));
        let form_enctype = $(this).attr("enctype");
        console.log(post_url);
        show_loader(true);
        $.ajax({
            url : post_url,
            type: request_method,
            data : data,
            enctype : form_enctype,
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                if(data.status === "ok") {
                    tmp = "";
                    if (data.data instanceof Array) {
                        for (er of data.data) {
                        tmp += er + "<br>";
                    }
                    } else {
                        tmp = data.data;
                    }
                    $("#error_"+form+" p").html(tmp);
                } else {
                    $("#error_"+form+" p").text(data.data);
                }
                step == 2;
                disable_form("config_2", false);
                var option = {value:data.dept_abbrev, text:data.dept_fullname} ;
                $('#dropdown_dpt_1').append($('<option>', option));
                $('#dropdown_dpt_2').append($('<option>', option));
                show_loader(false);
            },
            error: function (data) {
                console.log(data);
                // console.log(data.responseJSON.error);
                // $("#error_"+form+" p").text("Error : "+data.responseJSON.error);
                $("#error_"+form+" p").text("Error");
                show_loader(false);
            },
        })
    });
}

function disable_form(form, disable) {
    $("#"+form+" input").prop("disabled", disable);
}

send_form("config_1");
send_form("config_2");

if (step == 1) {
    disable_form("config_2", true)
}

function handleRadioChanges(value) {
    if (value === "1") {
        document.getElementById("depart_choice").innerHTML = "" +
            "<tr><th><label for=\"id_nom\">Nom:</label></th><td><input type=\"text\" name=\"nom\" required id=\"id_nom\"></td></tr>" +
            "<tr><th><label for=\"id_abbrev\">Abbrev:</label></th><td><input type=\"text\" name=\"abbrev\" maxlength=\"7\" required id=\"id_abbrev\"></td></tr>\n"
    } else if (value === "2") {
        opts = "";
        for(let dep of departements) {
            opts += "<option value='"+ dep.abbrev +"'>" + dep.name + "</option>\n"
        }
        document.getElementById("depart_choice").innerHTML = "" +
            "<select name='abbrev'>\n" +
            opts +
            "</select>"
    }
}

function init_departement_manager() {
    rBut = document.querySelector("#config_1 input[type=radio]:checked");
    if (rBut === null) {
        rBut = document.querySelector("#config_1 input[type=radio]");
        rBut.checked = true
    }
    handleRadioChanges(rBut.value);
}

document.querySelectorAll("#config_1 input[type=radio]").forEach((i) => {
    i.addEventListener('change', (event) => {
        handleRadioChanges(event.target.value);
    })
})

init_departement_manager();