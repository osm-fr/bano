#!/usr/bin/env python
# coding: UTF-8
import os
import psycopg2
from pg_connexion import get_pgc

pgc = get_pgc()
cur_dept = pgc.cursor()
cur_comm = pgc.cursor()

str_query = 'SELECT DISTINCT cadastre_dept FROM code_cadastre WHERE dept IS NOT NULL;'
# str_query = 'SELECT DISTINCT cadastre_dept FROM code_cadastre WHERE dept = \'67\';'
cur_dept.execute(str_query)
for d in cur_dept:
	str_query = 'SELECT cadastre_com,insee_com,nom_com,format_cadastre FROM code_cadastre WHERE cadastre_dept = \'{:s}\' ORDER BY 1;'.format(d[0])
	cur_comm.execute(str_query)
	fnosm = 'shells/load_cumul_{:s}_OSM.sh'.format(d[0])
	fncad  = 'shells/load_cumul_{:s}_CAD.sh'.format(d[0])
        fosm = open(fnosm,'wb')
        fcad = open(fncad,'wb')
        fosm.write('#!/bin/bash\n')
	fcad.write('#!/bin/bash\n')
	for c in cur_comm:
		if c[3] == 'VECT':
			fcad.write('python ../addr_2_db.py {:s} {:s} CADASTRE\n'.format(c[1],c[0]))
		fosm.write('python ../addr_2_db.py {:s} {:s} OSM\n'.format(c[1],c[0]))
	fosm.close()
        fcad.close()
        os.chmod(fnosm,0777)
	os.chmod(fncad,0777)
