#!/usr/bin/env python
# coding: UTF-8

import parcelles_buildings_2_db as a
import sys
import os

if len(sys.argv) != 1:
        print('USAGE : ./import_parcelles_buildings.py')
        os._exit(0)

pgc = a.get_pgc()

# On ne traite que les communes dont l'import initial est posterieur au dernier import de bâtiments
str_query = "SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c JOIN (SELECT cadastre_com FROM code_cadastre  WHERE format_cadastre = 'VECT' EXCEPT SELECT b1.cadastre_com FROM batch b1 JOIN batch b2 USING (cadastre_com) WHERE b1.etape = 'importQadastre' AND b2.etape = 'importBuildings' AND b1.timestamp_debut < b2.timestamp_debut)j USING (cadastre_com) ORDER BY 3,2;"

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[0]+' '+c[1])
	a.main(['','{:s}'.format(c[0])])
