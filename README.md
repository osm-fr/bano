bano
====

Différents outils pour la constitution de la Base Adresses Nationale Ouverte

v3 à venir :
- unification des adresses voies & lieux-dits
- gestion des communes fusionnées
- remplacement de FANTOIR par TOPO
- etc

## Dépendances

Il faut pour alimenter la base OSM locale dans laquelle puise BANO :
* [imposm](https://github.com/omniscale/imposm3) pour le chargement. Par défaut la dernière version.
* [osmosis](https://github.com/openstreetmap/osmosis) pour la mise à jour incrémentale. Par défaut la dernière version.

Autres outils : parallel.

## Configuration

Première étape avant de lancer les chargements de données : il faut adapter le fichier `config` à votre environnement, en déclarant différents chemins. Ce fichier est utilisé en début de plusieurs scripts pour connaître le chemin de différents répertoires.

### Création des répertoires
Une fois le fichier `config` rempli, lancer la création des répertoires avec :
```
arborescence.sh
```

### Liste des départements

Les départements pris en compte sont listés dans `deplist.txt`. Cette liste peut être modifiée.

### Création de la base de données

La base de données qui accueille toutes les données BANO (les sources et les données produites) s'appelle 'bano' est doit être créée en début d'installation. C'est l'utilisateur 'postgres' qui doit exécuter les scripts de création de la base.

```
sudo -u postgres -s "./create_base.sh"
```
On utilise ensuite le module python 'bano' pour terminer la configuration de la BD :
```
bano setup_db
```
À l'issue de cette étape toutes les tables nécessaires existent dans la BD. Elles sont toutes vides.

## Chargement des données OSM
### Chargement initial
D'abord renseigner le fichier imposm.config, puis lancer :
```
./load_osm_france_db.sh
```
À l'issue, les tables du schéma osm sont remplies.

### Mise à jour en continu

## Chargement des autres données sources
Chaque source a sa commande de chargement
### TOPO (ex FANTOIR)
```
bano charge_topo_sas --version topo

puis vérification manuelle des deltas via la table topo_comparaison. Si ok :

bano publish_topo
```
### BAN
```
bano charge_ban
bano update_bis_table
```
### COG
```
bano charge_cog
```
### Lieux-dits du Cadastre
```
bano charge_ld_cadastre
```
### Communes du cadastre
```
bano charge_communes_cadastre
```

## QA - Validation du résultat

Statistiques entre deux versions différentes de la BANO pour évaluer la différence.
Compare les publications en format JSON. Avec optionnellement un JSON spécifique à comparer dans répertoire (département).

```
./bano-diff.sh ancienne_bano/data/work/bano.openstreetmap.fr/www/web/data/full.sjson.gz nouvelle_bano/data/work/bano.openstreetmap.fr/www/web/data/full.sjson.gz
```
