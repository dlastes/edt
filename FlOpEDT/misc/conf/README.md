## Installation et lancement de l'application sans docker

Ce qui suit est une proposition d'installation avec un environnement
virtuel python et une base de données PostgreSQL. D'autres
configurations sont possibles.

### Installations Python/Django

- Récupérer le module pour gérer les environnements virtuels
`pip install virtualenv`
- Créer un env virtuel quelque part, par exemple :
`cd FlOpEDT`
`virtualenv -p /usr/bin/python3.6 venv`
- y aller
`source venv/bin/activate`
- Mettre à jour pip
`pip install --upgrade pip`
- Installer les modules python du requirements.txt
`pip install -r requirements.txt`
- Et éventuellement
`pip install python-memcached`
`pip install ipython`
`pip install daphne`
- sortir de l'env virtuel
`deactivate`


### Installation/configuration PostgreSQL 

- Installer postgre
`sudo apt-get install postgresql`
- Se logger avec l'utilisateur postgres pour toute la suite.
`sudo -i -u postgres`
- Regarder les infos de la database que django va utiliser dans [les
settings](https://framagit.org/flopedt/FlOpEDT/blob/master/FlOpEDT/FlOpEDT/settings/local.py). Chercher
la DATABASE par defaut : admettons qu'elle a un nom flopdb, un user
flopuser et un mot de passe floppwd. Utiliser ces informations pour la
suite.
- Créer l'utilisateur pour flop,
`createuser -P flopuser`,
et renseignez le mot de passe `pwddb`.
- Créer la base pour flop :
`createdb flopdb`
- Aller configurer la base. Lancer postgresql
`psql`,
et dans la console PSQL, octroyer à l'utilisateur les droits sur la base :
`GRANT ALL PRIVILEGES ON DATABASE flopdb TO flopuser;`
- Sortir de la console PSQL (par exemple Ctrl+d).

### Installation d'un solveur de programmes linéaires

#### CBC

#### Gurobi


### Initialisation Django

Django a été installé dans un environnement virtuel python, donc
toutes les actions concernant python devront être effectuées dans cet
environnement virtuel.

- Aller dans l'environnement virtuel
`source venv/bin/activate`
- /Pour une première exécution/, 
 + appliquer les migrations :
`sudo ./manage.py migrate`
 + éventuellement, remplir la base avec les données d'exemple :
`sudo ./manage.py loaddata ../dump.json`
 + pour supprimer ces données :
 `sudo ./manage.py flush`

### Exécution en local

- Lancer django
`sudo ./manage.py runserver`
- Accéder au site depuis un navigateur en tapant l'adresse :
`localhost:8000`
(dans les données d'exemple, la semaine 36 contient des cours. Pour y accéder :
`http://localhost:8000/edt/INFO/2019/36`)

### Exécution sur le serveur de production

- Installer nginx
`sudo apt install nginx`

- Configurer nginx : un exemple de configuration nginx est disponible
[ici](https://framagit.org/flopedt/FlOpEDT/blob/master/FlOpEDT/misc/conf/edt-info.conf).
Remplacer `adresse_du_site` par l'adresse du serveur.

- Configurer un service : un exemple de configuration se trouve
[ici](https://framagit.org/flopedt/FlOpEDT/blob/master/FlOpEDT/misc/conf/flopedt.service).
Remplacer `path_to_where_manage_belongs_to` par le bon chemin.
Par ailleurs, dans le cas d'une utilisation de Gurobi, il faut rajouter [quelques
informations](https://framagit.org/flopedt/FlOpEDT/blob/master/FlOpEDT/misc/conf/flopedt.add)
à la fin de la section "[Service]" du fichier de configuration du service.

- Dans l'environnement virtuel python, rendre disponible les
  fichiers javascript notamment :
`sudo ./manage.py collectstatic`

- Lancer le service :
`sudo start flopedt`

- Le site devrait être accessible depuis l'extérieur à l'adresse
  `adresse_du_site`.
