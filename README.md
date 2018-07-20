![Logo](./FlOpEDT/base/static/base/img/flop2.png)

FlOpEDT/FlOpScheduler est un outil de gestion
d'emplois du temps comprenant :
- une application web permettant aux utilisateurs
  * d'exprimer leurs contraintes et préférences
  * de modifier l'emploi du temps
- un moteur de génération d'emplois du temps qui respectent les contraintes et
maximisent la satisfaction générale.

![Aperçu de la vue d'accueil](./img/edt-accueil.jpg)
![Aperçu de la vue de changement des disponibilités (/préférences)](./img/edt-dispos.jpg)

## Licence

[AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html)

## Principales dépendances
- [Django](https://www.djangoproject.com/) pour le site
- [PostgreSQL](https://www.postgresql.org/) pour la base de données
- [PuLP](https://github.com/coin-or/pulp) pour la modélisation en ILP (Integer Linear Programming)
- Un solveur de ILP, e.g. [CBC](https://projects.coin-or.org/Cbc), [Gurobi](gurobi.com)
- [Redis](https://redis.io) pour le cache de Django (optionnel)

## Lancement de l'application dans Docker

Après l'installation de `docker` et `docker-compose`, lancez la commande suivante pour récupérer les images de base et générer les containers. Cette commande n'est à exécuter qu'une seule fois et peut prendre un peu de temps.

`make build` 

Ensuite, vous pourrez lancer le serveur à l'aide de la commande:

`make start` (`make stop` pour arrêter l'application)

L'application sera accessible à l'adresse http://localhost:8000.

Vous pouvez importer le fichier dumpPy3.json (qui est une base pour jouer avec l'interface) avec la commande :

`make init` 

Vous pourrez alors vous connecter avec l'utilisateur 'MOI' et le mot de passe 'passe'. (En fait, tous les utilisateurs ont le même mot de passe !)

Les paramètres de la configuration courante se trouvent dans `FlOpEDT/settings`. Par défaut, on utilise la configuration `development`. On peut spécifier une autre configuration en modifiant la variable d'environnement `CONFIG` comme suit :

`export CONFIG=production && make start`

## Contributions
- [Discuter](https://flopedt.slack.com)
- [Soulever une issue](https://framagit.org/FlOpEDT/FlOpEDT/issues)


