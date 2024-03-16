psql -d bano -U cadastre -c "SELECT * FROM batch WHERE source = 'pifometre' ORDER BY timestamp_debut DESC LIMIT 10;"
psql -d bano -U cadastre -c "SELECT * FROM batch ORDER BY timestamp_debut DESC LIMIT 10;"
psql -d bano -U cadastre -c "SELECT * FROM batch WHERE not ok ORDER BY timestamp_debut DESC LIMIT 10;"
ps -eaf|grep -i bano
