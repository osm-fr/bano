sudo -u postgres -s
createuser -s -d cadastre
createdb -E UTF-8 -T template0 -O cadastre cadastre
exit
psql -d cadastre -U cadastre -f sql/create_base.sql
psql -d cadastre -U cadastre -f sql/create_table.sql
