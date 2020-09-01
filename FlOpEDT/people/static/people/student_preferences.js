// Text for morning preferences
// Text for preferences concerning day length
function txt_morning_half(val, id) {
  if (id == 'morning') {
    switch (val) {
    case "0":
        return 'Commencer le plus tôt possible mais finir tôt';
    case "0.25":
        return 'Ne pas commencer trop tard et ne pas finir trop tard';
        break;
    case "0.5":
        return 'Ni trop tôt ni trop tard';
        break;
    case "0.75":
        return 'Ne pas commencer trop tôt et finir plus tard';
        break;
    case "1":
        return 'Commencer le plus tard possible mais finir tard';
        break;
    default:
        return val;
    }
  } else {
    switch (val) {
    case "0":
        return 'Avoir toute la semaine des journées allégées';
        break;
    case "0.25":
        return 'Avoir plus de journées allégées que de demi-journées libérées';
        break;
    case "0.5":
        return 'Avoir des semaines équilibrées';
        break;
    case "0.75":
        return 'Avoir plus de demi-journées libérées que de journées allégées';
        break;
    case "1":
        return 'Avoir des journées chargées mais aussi des demi-journées libérées';
        break;
    default:
        return val;
    }
  }
}


// update comments associated with range value
function update_comment(id) {
  return function () {
    
    var txt = txt_morning_half($('#'+id).val(), id);
        $('#'+id).next().text(txt);
    } ;
}

// main
$(function() {
    var ids = ['morning', 'free_half_day'] ;
    ids.forEach(function(id) {
        $('#'+id).on('input', update_comment(id));
        $(document).ready(update_comment(id));
    });
});
