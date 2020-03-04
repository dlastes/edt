function exporter() {
    var value ;
    alert("Envoyer");
    var dico1 = new Map();
    var dico2 = new Map();

    dico1.set('tutor',user);

    for (t in donnees.roomtypes){
        var pref = [];
        for (s of donnees.roomtypes[t]){
            var temp = new Map();
            temp.set('roomgroup', s);
            value = $('#rooms-table #' + t
                      + ' #' +s).find(":selected").val() ;
            temp.set('value', value);
            pref.push(temp);
        }
        dico2.set(t,pref);
    }
    dico1.set('roompreferences', dico2);

    console.log(dico1);

}
