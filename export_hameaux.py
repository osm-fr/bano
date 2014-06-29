#!/usr/bin/env python
# coding: UTF-8
from pg_connexion import get_pgc
# from pg_connexion import get_pgc_layers
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import os,os.path
import sys
import time 
import xml.etree.ElementTree as ET

pgc = get_pgc()
str_query = 'SELECT ST_AsGeojson(geometrie),libelle_hameau,insee_com FROM hameaux;'
cur = pgc.cursor()
cur.execute(str_query)

fout = os.path.join(os.path.dirname(__file__),'hameaux.geojson')
f = open(fout,'wb')
f.write('{ "type": "FeatureCollection",\n  "features": [\n')

a_res = []
for c in cur:
	print(c[1])
	a_res.append('{{"type": "Feature",\n    "geometry":{:s},\n    "properties": {{\n    "hameau": "{:s}"}}\n}}'.format(c[0],c[1]))
f.write((',\n'.join(a_res)).decode('utf8').encode('utf8'))
f.write(']}')
f.close()
