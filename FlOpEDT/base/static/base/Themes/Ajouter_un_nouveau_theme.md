## Pour ajouter un thème :
- Créer un fichier css dans `FlOpEDT/base/static/base/Themes` en reprenant un exemple d'un thème existant pour plus de faciliter
- Dans `FlOpEDT/base/models.py` ajouter une paire clé valeur pour la classe Theme correspondant à votre thème
- Dans `FlOpEDT/templates/base.html` ajouter une condition à la suite des autres en haut du fichier pour charger le fichier que vous avez créé