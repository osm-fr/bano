find /data/work/cadastre.openstreetmap.fr/data/ -name *liste.txt |xargs -I {} cat {} > code_cadastre.txt
psql -d cadastre -f create_code_cadastre.sql
