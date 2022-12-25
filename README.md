# BANO

Différents outils pour la constitution de la Base Adresses Nationale Ouverte.

BANO est un ensemble de code python, shell et SQL. En l'état il faut comme pré-requis pour faire tourner BANO :
* 2 bases PostgreSQL avec les extensions postgis et hstore.
* Python : la version minimale théorique est 3.6, la version testée est 3.7.3.
* Environ 100Go pour les BD PostgreSQL.
* Environ 30 Go pour les fichiers plats (données source).

L'organisation générale est la suivante :
* Téléchargement des sources de données Adresse et OSM.
* Alimentation de la base de cache, nommée "osm" avec ces sources.
* Traitements python pour extraire de cette base les infos d'adresse et alimentation de la base de résultat, nommée "cadastre".
* Export des données constituées, dans différents formats (CSV, JSON, TTL, SHP).

## Dépendances

Il faut pour alimenter la base OSM locale dans laquelle puise BANO :
* [imposm](https://github.com/omniscale/imposm3) pour le chargement. Par défaut la dernière version.
* [osmosis](https://github.com/openstreetmap/osmosis) pour la mise à jour incrémentale. Par défaut la dernière version.

Autres outils : parallel.

## Configuration

Première étape avant de lancer les chargements de données : il faut adapter le fichier `config` à votre environnement, en déclarant différents chemins. Ce fichier est utilisé en début de plusieurs scripts pour connaître le chemin de différents répertoires.

Dans le script `load_fantoir.sh` il faut indiquer l'URL du fichier source, qui change chaque trimestre.

Adapter également l'URL du COG dans `load_COG.sh` si besoin.

### Création de la base de données

Pour charger les données OSM avec imposm dans la BD `osm` il faut d'abord la créer. Ça se fait en exécutant le script qui crée les 2 BD "osm" et "cadastre".
```
sudo -u postgres -s "./create_base.sh"
./init_base.sh"
```

## Chargement des données OSM

Se placer dans le répertoire `DATA_DIR`, et appeler les scripts depuis là.

### Création de la base de données

Pour charger les données OSM avec imposm dans la BD `osm` il faut d'abord la créer. Ça se fait en exécutant le script `create_base.sh` qui crée les 2 BD "osm" et "cadastre".

Ensuite, possibilité de charger des données OSM depuis un pbf. Le script cible est `load_osm_france_db.sh`.

Possible de changer l'URL dans le script pour prendre un pbf plus petit.

## Utilisation

Pour connaître les commandes du module bano : `bano --help`.

Quasiment toutes les options sont utilisées dans le script `cron_bano`.
