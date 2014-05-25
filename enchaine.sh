cd /data/project/cadastre.openstreetmap.fr/bin/cadastre-housenumber/bano
python import_cadastre.py $1
python load_cumul.py $1 CADASTRE
python load_cumul.py $1 OSM
cd out
sh banout.sh $1

