psql -d bano -U cadastre -c "SELECT  * FROM batch ORDER BY timestamp_debut DESC LIMIT 10;"
psql -d bano -U cadastre -c "SELECT  * FROM batch WHERE not ok ORDER BY timestamp_debut DESC LIMIT 10;"
ps -eaf|grep 'bano'
ps -eaf|grep cumul

