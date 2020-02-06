/* jshint esversion: 6 */

function is_slug(string) {
    return /^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$/.test(string);
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
            console.log(response);
            $("#button-create-department").html(button_html);
        },
        error: function(error) {
            console.log(error);
            $("#button-create-department").html(button_html);
        },
    });
});

$("#button-create-department").click(function(){
    const inputNomDep = $("#inputNomDep");
    const inputAbbrev = $("#inputAbbrev");
    const inputResp = $("#inputResp");
    const error_div = $("#form-error-message");
    if(inputNomDep.val().length > 0 && inputNomDep.val().length <= 50) {
        if(is_slug(inputAbbrev.val()) && inputAbbrev.val().length <= 7) {
            if(inputResp[0].selectedIndex !== 0) {
                error_div.hide();
                $("#form-create-department").submit();
            } else {
                error_div.text("Vous devez séléctionner un responsable.");
                error_div.show();
            }
        } else {
            error_div.text("L'abréviation du département est invalide. Elle peut comporter des lettres et des chiffres. Elle ne doit pas comporter d'espace, utilisez des '-' pour les séparations.");
            error_div.show();
        }
    } else {
        error_div.text("Le nom du département est invalide. Il doit comporter entre 1 et 50 caractères.");
        error_div.show();
    }
});
