#find /data/work/cadastre.openstreetmap.fr/data/ -name *liste.txt |xargs -I {} cat {} > code_cadastre.txt
python create_code_cadastre.py
psql -d cadastre -f create_code_cadastre.sql
