function exporter() {
  var value, value_dict;

  var sent_data = {};

  var pref = {};
  for (t in init_pref) {
    value_dict = {};
    console.log(t);
    for (s in init_pref[t]) {
      value = +$('#rooms-table #' + t + ".rooms"
        + ' #' + s + ".pref").find(":selected").val();
      value_dict[s] = value;
      console.log(s + ' -> ' + value);
    }
    if (Object.keys(value_dict).length > 0) {
      pref[t] = value_dict;
    }
  }

  sent_data['roompreferences'] = JSON.stringify(pref);

  console.log(sent_data);
  $.ajax({
    url: url_changes,
    type: 'POST',
    data: sent_data,
    dataType: 'json',
    success: function (msg) {
      $("#ack").text("Opération réussie.");
    },
    error: function (msg) {
      $("#ack").text("C'est un échec. " + msg);
    }
  });

}

