#!/usr/bin/env python
# coding: UTF-8

import parcelles_buildings_2_db as a
import sys
import os

if len(sys.argv) != 2:
        print('Mauvais nombre d\'arguments')
        print('USAGE : ./import_parcelles_buildings.py <numero de dept|FRANCE>')
        os._exit(0)

clause_where = ''
if sys.argv[1].upper() != 'FRANCE':
	num_dept_cadastre = ('000'+sys.argv[1])[-3:]
	clause_where = 'AND cadastre_dept = \'{:s}\''.format(num_dept_cadastre)
	
pgc = a.get_pgc()
#str_query = 'SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c LEFT OUTER JOIN (SELECT cadastre_com FROM batch WHERE etape = \'{:s}\' AND date_fin IS NOT NULL AND nombre_adresses > 0 INTERSECT SELECT cadastre_com FROM batch WHERE etape = \'{:s}\' AND date_fin IS NOT NULL AND nombre_adresses > 0 ) j ON c.cadastre_com = j.cadastre_com WHERE j.cadastre_com IS NULL AND c.format_cadastre = \'VECT\' {:s} ORDER BY 3,2;'.format('importParcelles','importBuildings',clause_where)
#str_query = "SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c JOIN (SELECT cadastre_com FROM code_cadastre  WHERE format_cadastre = 'VECT' {:s}  EXCEPT SELECT b1.cadastre_com FROM batch b1 JOIN batch b2 USING (cadastre_com) WHERE b1.etape in ('importParcelles','importBuildings') AND b2.etape = 'recupCadastre' AND b1.timestamp_debut > b2.timestamp_debut)j USING (cadastre_com) ORDER BY 3,2;".format(clause_where)
#str_query = "SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c WHERE format_cadastre = 'VECT' {:s}  ORDER BY 3,2;".format(clause_where)

# On ne traite que les communes dont l'import initial est posterieur au dernier import de bâtiments
str_query = "SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c JOIN (SELECT cadastre_com FROM code_cadastre  WHERE format_cadastre = 'VECT' {:s}  EXCEPT SELECT b1.cadastre_com FROM batch b1 JOIN batch b2 USING (cadastre_com) WHERE b1.etape = 'importQadastre' AND b2.etape = 'importBuildings' AND b1.timestamp_debut < b2.timestamp_debut)j USING (cadastre_com) ORDER BY 3,2;".format(clause_where)

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[0]+' '+c[1])
	a.main(['','{:s}'.format(c[0])])
