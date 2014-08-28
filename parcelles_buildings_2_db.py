#!/usr/bin/env python
# coding: UTF-8
from addr_2_db import get_code_cadastre_from_insee
from addr_2_db import get_cadastre_code_dept_from_insee
from addr_2_db import get_tags
from pg_connexion import get_pgc
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import gc
import glob
import os,os.path
import sys
import time 
import xml.etree.cElementTree as ET

class Node:
	def __init__(self,attribs,tags):
		self.attribs = attribs
		self.tags = tags
		self.sent = False
		self.modified = False
class Nodes:
	def __init__(self):
		self.n = {}
		self.min_id = 0
	def load_xml_node(self,xml_node,tags):
		id = str(xml_node.attrib['id'])
		if 'version' not in xml_node.attrib:
			xml_node.attrib['version'] = '0'
		self.n[id]= Node(xml_node.attrib,tags)
		self.min_id = min(self.min_id,int(id))
class Way:
	def __init__(self,geom,tags,attrib,osm_key):
		self.geom = geom
		self.tags = tags
		self.attrib = attrib
		self.modified = False
		self.sent = False
		self.is_valid = True
		self.checks_by_osm_key(osm_key)
	def checks_by_osm_key(self,osm_key):
		if osm_key == 'building':
			self.set_wall()
	def set_wall(self):
		if 'wall' not in self.tags:
			self.wall = 'yes'
		else:
			self.wall = self.tags['wall']
	def get_as_SQL_import_building(self):
		str_query = 'INSERT INTO tmp_buildings (SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText({:s})),4326),900913),							\'{:s}\',\'{:s}\');'.format(self.geom.get_geom_as_linestring_text(),code_insee,self.wall)
		return str_query
	def get_as_SQL_import_parcelle(self):
		str_query = ''
		a_values = []
		id_cadastre = ''
		if 'ref:FR:CADASTRE:PARCELLE' in self.tags:
			id_cadastre = self.tags['ref:FR:CADASTRE:PARCELLE']
		for i in range(0,9):
			voie = ''
			numero = ''
			fantoir = ''
			street_tag = 'addr{:d}:street'.format(i)
			hsnr_tag = 'addr{:d}:housenumber'.format(i)
			if not street_tag in self.tags and not hsnr_tag in self.tags:
				break
			if street_tag in self.tags:
				voie = self.tags[street_tag].replace('\'','\'\'')
			else:
				continue
			if hsnr_tag in self.tags:
				numero = self.tags[hsnr_tag]
			a_values.append('(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText({:s})),4326),900913)),\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\''.format(self.geom.get_geom_as_linestring_text(),code_insee,id_cadastre,numero,voie,fantoir))
		if a_values:
			str_query = 'INSERT INTO parcelles VALUES ({:s});'.format('),('.join(a_values))
		return str_query
class WayGeom:
	def __init__(self,a_nodes):
		self.a_nodes = a_nodes
	def get_geom_as_linestring_text(self):
		res = '\'LINESTRING('
		a_n = []
		for ni in self.a_nodes:
			a_n.append(str(nodes.n[ni].attribs['lon'])+' '+str(nodes.n[ni].attribs['lat']))
		res = res+','.join(a_n)+')\''
		return res	
class Ways:
	def __init__(self):
		self.w = {'highway':{},
				'building':{},
				'parcelle':{}}
	def add_way(self,w,id,osm_key):
		self.w[osm_key][id] = w
def create_tmp_building_table():
	str_query = "CREATE TEMP TABLE tmp_buildings(geometrie geometry,insee_com character varying(5),wall character varying(3));"
	cur = pgc.cursor()
	cur.execute(str_query)
def get_cache_directory(insee_com,cadastre_com):
	cadastre_dep = get_cadastre_code_dept_from_insee(insee_com)
	cache_directory = os.path.join('/data/work/cadastre.openstreetmap.fr/bano_cache/',cadastre_dep,cadastre_com)
	return cache_directory
def load_nodes_from_xml_parse(xmlp):
	for n in xmlp.iter('node'):
		dtags = get_tags(n)
		nodes.load_xml_node(n,dtags)
def load_parcelles(fnparcelles):
	xmlparcelles = ET.parse(fnparcelles)
	load_nodes_from_xml_parse(xmlparcelles)
	load_ways_from_xml_parse(xmlparcelles,'parcelle')
	del xmlparcelles
	gc.collect()

	sys.stdout.flush()
	cur_parcelles = pgc.cursor()
	str_query = "DELETE FROM parcelles WHERE insee_com = '{:s}';".format(code_insee)
	for idx,id in enumerate(ways.w['parcelle']):
		str_query = str_query+ways.w['parcelle'][id].get_as_SQL_import_parcelle()
		if idx%100 == 0:
			cur_parcelles.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_parcelles.execute(str_query+"COMMIT;")
	return len(ways.w['parcelle'])
def load_tmp_buildings(fnbuildings):
	xmlbuildings = ET.parse(fnbuildings)
	load_nodes_from_xml_parse(xmlbuildings)
	load_ways_from_xml_parse(xmlbuildings,'building')
	del xmlbuildings
	gc.collect()

	sys.stdout.flush()
	cur_building = pgc.cursor()
	str_query = ""
	for idx,id in enumerate(ways.w['building']):
		str_query = str_query+ways.w['building'][id].get_as_SQL_import_building()
		if idx%100 == 0:
			cur_building.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_building.execute(str_query+"COMMIT;")
	return len(ways.w['building'])
def load_buildings():
	cur_building = pgc.cursor()
	str_query = "DELETE FROM buildings WHERE insee_com = '{:s}';INSERT INTO buildings(geometrie,insee_com,wall) SELECT DISTINCT geometrie,insee_com,wall FROM tmp_buildings;".format(code_insee)
	cur_building.execute(str_query+"COMMIT;")
def load_ways_from_xml_parse(xmlp,osm_key):
	for b in xmlp.iter('way'):
		a_n = []
		for bn in b.iter('nd'):
			a_n.append(bn.get('ref'))
		g = WayGeom(a_n)
		dtags = get_tags(b)
		ways.add_way(Way(g,dtags,b.attrib,osm_key),b.get('id'),osm_key)
def main(args):
	global batch_id
	global pgc
	global code_insee,code_dept,cadastre_com
	global nodes,ways
	
	nodes = Nodes()
	ways = Ways()
	pgc = get_pgc()
	
	debut_total = time.time()
	usage = 'USAGE : python parcelles_buildings_2_db.py <code INSEE>'
	if len(args) != 2:
		print(usage)
		os._exit(0)
	code_insee = args[1]
	cadastre_com = get_code_cadastre_from_insee(code_insee)
	# cadastre_com = 'S0335'
	fn_parcelles = os.path.join(get_cache_directory(code_insee,cadastre_com),cadastre_com+'-parcelles.osm')
	# fn_parcelles = 'C:\\Users\\vincent\\Documents\\GitHub\\ZA063-parcelles.osm'
	batch_id = batch_start_log('CADASTRE','importParcelles',cadastre_com)
	nb_parcelles = load_parcelles(fn_parcelles)
	batch_end_log(nb_parcelles,batch_id)

	a_fn_houses_parts = glob.glob('{:s}/{:s}-[0-9]-[0-9]-houses.osm'.format(get_cache_directory(code_insee,cadastre_com),cadastre_com))
	# a_fn_houses_parts = glob.glob('{:s}\\{:s}-[0-9]-[0-9]-houses.osm'.format('C:\\Users\\vincent\\Documents\\GitHub','ZA063'))
	create_tmp_building_table()
	nb_buildings = 0
	batch_id = batch_start_log('CADASTRE','importBuildings',cadastre_com)
	for h in a_fn_houses_parts:
		print(h)
		nodes = Nodes()
		ways = Ways()
		nb_buildings += load_tmp_buildings(h)
	load_buildings()
	batch_end_log(nb_buildings,batch_id)
	pgc.close()
if __name__ == '__main__':
    main(sys.argv)
