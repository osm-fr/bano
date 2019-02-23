source config
cd $DATA_DIR
mkdir fantoir
cd fantoir
rm -rf FANTOIR*
wget https://static.data.gouv.fr/resources/fichier-fantoir-des-voies-et-lieux-dits/20190205-142621/fantoir0119.zip -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
psql -d osm -U cadastre -f $BANO_DIR/sql/load_fantoir.sql
