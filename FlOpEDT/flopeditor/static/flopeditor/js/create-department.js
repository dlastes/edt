/* jshint esversion: 6 */

function is_slug(string) {
    return /^[a-zA-Z]\w{0,6}$/.test(string);
}

function message_reset() {
  const message_div = $("#form-message");
  message_div.removeClass(function(index, className) {
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
  message_div.addClass("alert-"+msg_type);
  message_div.text(content);
  message_div.show();
}

$("#form-create-department").submit(function(event) {
    event.preventDefault();

    var form = $(this);
    var url = form.attr('action');

    const button_html = $("#button-create-department").html();
    $("#button-create-department").html("<i class=\"fas fa-spinner fa-pulse\"></i>");
    $.ajax({
        type: "POST",
        url: url,
        data: form.serialize(),
        success: function(response) {            
            $("#button-create-department").html(button_html);
            switch(response.status) {
              case 'OK':
                window.location.href = "";
                break;
              case 'ERROR':
                message_display("warning", response.message);
                break;
              case 'UNKNOWN':
                message_display("warning", response.message);
            }

        },
        error: function(error) {
            $("#button-create-department").html(button_html);
            message_display("warning", "Une erreur est survenue. Veuillez réessayer.");
        },
    });
});

$("#button-create-department").click(function(){
    const inputNomDep = $("#inputNomDep");
    const inputAbbrev = $("#inputAbbrev");
    const inputResp = $("#inputResp");
    if(inputNomDep.val().length > 0 && inputNomDep.val().length <= 50) {
        if(is_slug(inputAbbrev.val()) && inputAbbrev.val().length <= 7) {
            if(inputResp[0].selectedIndex !== 0) {
                message_hide();
                $("#form-create-department").submit();
            } else {
                message_display("warning", "Vous devez sélectionner un responsable.");
            }
        } else {
            message_display("warning", "L'abréviation du département est invalide. Elle doit être entre 1 et 7 caractères. Elle peut comporter des lettres et des chiffres et doit commencer par une lettre. Elle ne doit pas comporter d'espace, utilisez des '_' pour les séparations.");
        }
    } else {
        message_display("warning", "Le nom du département est invalide. Il doit comporter entre 1 et 50 caractères.");
    }
});
