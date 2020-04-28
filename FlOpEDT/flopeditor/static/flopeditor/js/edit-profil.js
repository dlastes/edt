/* jshint esversion: 6 */

function message_reset2() {
    const message_div = $("#form-message-profil");
    message_div.removeClass(function (index, className) {
        return (className.match(/(^|\s)alert-\S+/g) || []).join(' ');
    });
    message_div.text("");
}



function message_display2(msg_type, content) {
    message_reset2();
    const message_div = $("#form-message-profil");
    message_div.addClass("alert-" + msg_type);
    message_div.text(content);
    message_div.show();
}


$('#modal-profil-edit').on('show.bs.modal', function(e){
  checkVacataireOrFullStaff();
});

function checkVacataireOrFullStaff() {
  var statusSelect = document.getElementById('newInputStatus');
  var strUser = statusSelect.options[statusSelect.selectedIndex].text;
  var idStatusVacataire = document.getElementById('statusVacataire');
  var idEmployer = document.getElementById('employer');
  var idIsIut = document.getElementById('is_iut_checkbox');
  if(strUser=='Vacataire') {
      idStatusVacataire.style.display = "block";
      idEmployer.style.display = "block";
      idIsIut.style.display = "none";
  } else if(strUser=='Permanent'){
      idStatusVacataire.style.display = "none";
      idEmployer.style.display = "none";
      idIsIut.style.display = "block";
  } else {
    idStatusVacataire.style.display = "none";
    idEmployer.style.display = "none";
    idIsIut.style.display = "none";
  }

}

$('#validerProfil').click(function(){
  var elements = document.getElementById("form-profil").elements;
  var id = elements.namedItem("newIdProfil").value;
  console.log(id);
  var firstName = elements.namedItem("newFirtNameProfil").value;
  console.log(firstName);
  var lastName = elements.namedItem("newSecondNameProfil").value;
  console.log(lastName);
  var email = elements.namedItem("newEmailProfil").value;
  console.log(email);
  var status = elements.namedItem("newInputStatus").value;
  console.log(status);
  var statusVacataire = null;
  var employer = null;
  if (status == 'Vacataire') {
    statusVacataire = elements.namedItem("newStatusVacataire").value;
    console.log(statusVacataire);
    employer = elements.namedItem("newEmployer").value;
    console.log(employer);
  }

})


$('#form-profil').submit(function(event) {

  event.preventDefault();
  var form = $(this);
  var url = form.attr('action');
  $("#validerProfil").addClass('disabled');
  $("#cancel-profil").addClass('disabled');
  const button_html = $("#validerProfil").html();
  $("#validerProfil").html("<i class=\"fas fa-spinner fa-pulse\"></i>");
  $.ajax({
      type: "POST",
      url: url,
      data: form.serialize(),
      success: function(response) {
          $("#validerProfil").html(button_html);
          switch(response.status) {
            case 'OK':
              $("#validerProfil").removeClass('disabled');
              $("#cancel-profil").removeClass('disabled');
              window.location.href = "";
              break;
            case 'ERROR':
              $("#validerProfil").removeClass('disabled');
              $("#cancel-profil").removeClass('disabled');
              message_display2("warning", response.message);
              break;
            case 'UNKNOWN':
              $("#validerProfil").removeClass('disabled');
              $("#cancel-profil").removeClass('disabled');
              message_display2("warning", response.message);
              break;
          }

      },
      error: function(error) {
          $("#validerProfil").html(button_html);
          message_display2(form, "warning", "Une erreur est survenue. Veuillez réessayer.");
      },
  });
});
