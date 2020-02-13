/* jshint esversion: 6 */

function is_time(string) {
    return /^[0-2][0-9]:[0-5][0-9]$/.test(string);
}

function message_reset() {
    const message_div = $("#form-message");
    message_div.removeClass(function (index, className) {
        return (className.match(/(^|\s)alert-\S+/g) || []).join(' ');
    });
    message_div.text("");
}

function message_hide() {
    const message_div = $("#form-message");
    message_div.hide();
    message_reset();
}

function message_display(msg_type, content) {
    message_reset();
    const message_div = $("#form-message");
    message_div.addClass("alert-" + msg_type);
    message_div.text(content);
    message_div.show();
}

$("#form-parameters").submit(function (event) {
    event.preventDefault();

    var form = $(this);
    var url = form.attr('action');

    var days = [];
    $.each($("input[name='days']:checked"), function () {
        days.push($(this).val());
    });
    if (days.length <= 0) {
        message_display("warning", "Veuillez cocher au moins un jour");
    } else if (!is_time($("#day_start_time").val())) {
        message_display("warning", "L'heure de début des cours est incorrecte.");
    } else if (!is_time($("#day_finish_time").val())) {
        message_display("warning", "L'heure de fin des cours est incorrecte.");
    } else if (!is_time($("#lunch_break_start_time").val())) {
        message_display("warning", "L'heure de début du déjeuner est incorrecte.");
    } else if (!is_time($("#lunch_break_finish_time").val())) {
        message_display("warning", "L'heure de fin du déjeuner est incorrecte.");
    } else if (!is_time($("#default_preference_duration").val())) {
        message_display("warning", "La durée par défaut d'un cours est incorrecte.");
    } else if ($("#day_start_time").val() > $("#day_finish_time").val()) {
        message_display("warning", "L'heure de début des cours doit précéder l'heure de fin des cours.");
    } else if ($("#lunch_break_start_time").val() > $("#lunch_break_finish_time").val()) {
        message_display("warning", "L'heure de début du déjeuner doit précéder l'heure de fin du déjeuner.");
    } else if ($("#day_start_time").val()> $("#lunch_break_start_time").val() || $("#lunch_break_finish_time").val() > $("#day_finish_time").val()) {
        message_display("warning", "La période du déjeuner doit être pendant la période des cours.");
    } else if ($("#default_preference_duration").val() === "00:00") {
        message_display("warning", "La durée par défaut d'un cours ne peut pas être nulle.");
    }
    else {
        const button_html = $("#button-submit").html();
        $("#button-submit").html("<i class=\"fas fa-spinner fa-pulse\"></i>");
        $.ajax({
            type: "POST",
            url: url,
            data: form.serializeArray(),
            success: function (response) {
                $("#button-submit").html(button_html);
                switch (response.status) {
                    case 'OK':
                        message_display("success", response.message)
                        break;
                    case 'ERROR':
                        message_display("warning", response.message);
                        break;
                    case 'UNKNOWN':
                        message_display("warning", response.message);
                }

            },
            error: function (error) {
                $("#button-submit").html(button_html);
                message_display("warning", "Une erreur est survenue. Veuillez réessayer.");
            },
        });
    }
});

$("#button-create-depdddddartment").click(function () {
    const inputNomDep = $("#inputNomDep");
    const inputAbbrev = $("#inputAbbrev");
    const inputResp = $("#inputResp");
    if (inputNomDep.val().length > 0 && inputNomDep.val().length <= 50) {
        if (is_slug(inputAbbrev.val()) && inputAbbrev.val().length <= 7) {
            if (inputResp[0].selectedIndex !== 0) {
                message_hide();
                $("#form-create-department").submit();
            } else {
                message_display("warning", "Vous devez sélectionner un responsable.");
            }
        } else {
            message_display("warning", "L'abréviation du département est invalide. Elle peut comporter des lettres et des chiffres. Elle ne doit pas comporter d'espace, utilisez des '-' pour les séparations.");
        }
    } else {
        message_display("warning", "Le nom du département est invalide. Il doit comporter entre 1 et 50 caractères.");
    }
});
