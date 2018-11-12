source config
cd $DATA_DIR
mkdir fantoir
cd fantoir
rm -rf FANTOIR*
wget https://static.data.gouv.fr/resources/fichier-fantoir-des-voies-et-lieux-dits/20180806-094626/FANTOIR0718.zip -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
psql -d cadastre -f $BANO_DIR/sql/load_fantoir.sql
