  $(function() {
	   $('.range').next().text('Veuillez sélectionner votre préférence.'); // Valeur par défaut
	    $('.range').on('input', function() {
		      var $set = $(this).val();

          switch ($set) {
            case "0":
              $set = 'Commencer le plus tôt possible mais finir tôt';
              break;
            case "0.25":
              $set = 'Ne pas commencer trop tard et ne pas finir trop tard';
              break;
            case "0.5":
              $set = 'Ni trop tôt ni trop tard';
              break;
            case "0.75":
              $set = 'Ne pas commencer trop tôt et finir plus tard';
              break;
            case "1":
              $set = 'Commencer le plus tard possible mais finir tard';
              break;
            default:
              $set = $set;
          }
		$(this).next().text($set);
	 });
  });

  $(function() {
	   $('.rangedeux').next().text('Veuillez sélectionner votre préférence.'); // Valeur par défaut
	    $('.rangedeux').on('input', function() {
		      var $set = $(this).val();

          switch ($set) {
            case "0":
              $set = 'Avoir toute la semaine des journées allégées';
              break;
            case "0.25":
              $set = 'Avoir plus de journées allégées que de demi-journées libérées';
              break;
            case "0.5":
              $set = 'Avoir des semaines équilibrées';
              break;
            case "0.75":
              $set = 'Avoir plus de demi-journées libérées que de journées allégées';
              break;
            case "1":
              $set = 'Avoir des journées chargées mais aussi des demi-journées libérées';
              break;
            default:
              $set = $set;
          }
		$(this).next().text($set);
	 });
  });
