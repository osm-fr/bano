source config
cd $DATA_DIR
mkdir fantoir
cd fantoir
rm -rf FANTOIR*
wget https://static.data.gouv.fr/resources/fichier-fantoir-des-voies-et-lieux-dits/20181107-134510/fantoir1018.zip -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
psql -d cadastre -U cadastre -f $BANO_DIR/sql/load_fantoir.sql
