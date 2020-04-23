/* jshint esversion: 6 */

function checkVacataire() {
  var statusSelect = document.getElementById('newInputStatus');
  var strUser = statusSelect.options[statusSelect.selectedIndex].text;
  var idStatusVacataire = document.getElementById('statusVacataire');
  var idEmployer = document.getElementById('employer');
  if(strUser=='Vacataire') {
      idStatusVacataire.style.display = "block";
      idEmployer.style.display = "block";
  } else {
      idStatusVacataire.style.display = "none";
      idEmployer.style.display = "none";
  }

}
