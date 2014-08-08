#!/usr/bin/env python
# coding: UTF-8
import sys
import time
import gc
import os,os.path
from pg_connexion import get_pgc
from addr_2_db import get_code_cadastre_from_insee
from addr_2_db import get_cadastre_code_dept_from_insee
from addr_2_db import get_nb_parts
from addr_2_db import get_part_debut
from addr_2_db import get_tags
# from addr_2_db import is_valid_housenumber
from addr_2_db import Node
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import xml.etree.ElementTree as ET

class Node:
	def __init__(self,attribs,tags):
		self.attribs = attribs
		self.tags = tags
		self.sent = False
		self.modified = False
	def get_geom_as_text(self):
		strp = 'ST_PointFromText(\'POINT('+str(self.attribs['lon'])+' '+str(self.attribs['lat'])+')\',4326)'
		return strp
	def move_to(self,lon,lat):
		self.attribs['lon'] = lon
		self.attribs['lat'] = lat
	def get_as_osm_xml_node(self):
		s = "\t<node id="+XSS.quoteattr(self.attribs['id'])
		if self.modified:
			s = s+" action=\"modify\" "
		for a in self.attribs:
			if a != 'id':
				if a == 'user':
					v = XSS.quoteattr(self.attribs[a]).encode('utf8')
				else:
					v = XSS.quoteattr(str(self.attribs[a]).encode('utf8'))
				s = s+" "+a+"="+v
		if len(self.tags) == 0:
			s = s+"/>\n"
		else:
			s = s+">\n"
			for k in sorted(self.tags.viewkeys()):
				s = s+"\t\t<tag k="+XSS.quoteattr(k)+" v="+XSS.quoteattr(self.tags[k]).encode('utf8')+"/>\n"
			s = s+"\t</node>\n"
		return s
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
	def load_new_node_from_xml(self,xml_node,tags):
		n = self.add_new_node(xml_node.attrib,tags)
		return n
	def add_new_node(self,lon,lat,tags):
		id = str(self.min_id - 1)
		attribs = {'lon':lon,'lat':lat,'version':0,'id':id}
		self.n[id] = Node(attribs,tags)
		self.n[id].modified = True
		self.min_id = min(self.min_id,int(id))
		return id
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
			self.check_valid_building()
		if osm_key == 'parcelle':
			self.collect_adresses()
	def set_wall(self):
		if 'wall' not in self.tags:
			self.wall = 'yes'
		else:
			self.wall = self.tags['wall']
	def check_valid_building(self):
		if len(self.geom.a_nodes) < 4:
			print('*** batiment invalide (au moins 4 points) Voir http://www.osm.org/way/'+self.attrib['id'])
			self.is_valid = False
		if self.is_valid and self.geom.a_nodes[0] != self.geom.a_nodes[-1]:
			print('*** batiment invalide (ouvert) Voir http://www.osm.org/way/'+self.attrib['id'])
			self.is_valid = False
	def collect_adresses(self):
		tmp_addrs = {}
		self.addrs = {}
		for t in self.tags.viewkeys():
			if t[0:4] == 'addr':
				num_addr = t.split(':')[0][4:]
				if not num_addr in tmp_addrs:
					tmp_addrs[num_addr] = {}
				tmp_addrs[num_addr]['addr:'+t.split(':')[1]] = self.tags[t]
		for sa in tmp_addrs.viewkeys():
			if 'addr:street' in tmp_addrs[sa]:
				self.addrs[sa] = tmp_addrs[sa]
				# dicts.add_voie('parcelle',tmp_addrs[sa]['addr:street'])
	def add_tag(self,k,v):
		self.tags[k] = v
		self.modified = True
	def insert_new_point(self,n_id,offset):
		b_geom = self.geom.a_nodes
		b_geom.insert(offset+1,n_id)
		self.geom.a_nodes = b_geom
		self.modified = True
	def get_as_osm_xml_way(self):
		s_modified = ""
		if self.modified:
			s_modified = "action=\"modify\" "
		s = "\t<way id=\""+self.attrib['id']+"\" "+s_modified
		for a in self.attrib:
			if a == 'id' or a == 'modify':
				continue
			else:
				if a == 'user':
					v = XSS.quoteattr(self.attrib[a]).encode('utf8')
				else:
					v = XSS.quoteattr(str(self.attrib[a]).encode('utf8'))
				#s = s+" "+a+"="+v
				s = s+" "+a.encode('utf8')+"="+v
		s = s+">\n"
		for nl in self.geom.a_nodes:
			s = s+"\t\t<nd ref=\""+str(nl)+"\" />\n"
		for k in sorted(self.tags.viewkeys()):
			s = s+"\t\t<tag k="+XSS.quoteattr(k)+" v="+XSS.quoteattr(self.tags[k]).encode('utf8')+"/>\n"
		s = s+"\t</way>\n"
		return s
	def get_as_SQL_import_building(self):
		str_query = '''INSERT INTO building_'''+code_insee+'''
							(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText('''+(self.geom.get_geom_as_linestring_text())+''')),4326),2154),
							'''+self.attrib['id']+''',\''''+self.wall+'''\');'''
		return str_query
	def get_as_SQL_import_building_segment(self,indice):
		s_stline = get_line_in_st_line_format([self.geom.a_nodes[indice],self.geom.a_nodes[indice+1]])
		str_query = '''INSERT INTO building_segments_'''+code_insee+''' 
						(SELECT ST_Transform(ST_SetSRID('''+s_stline+''',4326),2154),
						'''+self.attrib['id']+''',
						'''+self.geom.a_nodes[indice]+''',
						'''+self.geom.a_nodes[indice+1]+''',
						'''+str(indice)+''');'''
		return str_query
	def get_as_SQL_import_parcelle(self):

		street = ''
		if 'addr:street' in self.attrib:
			street = self.attrib['addr:street']
		str_query = ""
		for a in self.addrs:
			addr = ''
			if 'addr:housenumber' in self.addrs[a]:
				addr = self.addrs[a]['addr:housenumber']
			str_query = str_query+'''INSERT INTO parcelles_'''+code_insee+''' 
							(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText('''+(self.geom.get_geom_as_linestring_text())+''')),4326),900913),
							'''+self.attrib['id']+''',\''''+addr+'''\',\''''+self.addrs[a]['addr:street'].replace('\'','\'\'')+'''\');'''
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
def	executeSQL_INSEE(fnsql,code_insee):
	fsql = open(fnsql,'rb')
	str_query = fsql.read()
	fsql.close()
	str_query = str_query.replace('__com__','_'+code_insee)
	str_query = str_query.replace('#com__',code_insee)
	cur_sql = pgc.cursor()
	cur_sql.execute(str_query)
	cur_sql.close()
def load_nodes_from_xml_parse(xmlp):
	for n in xmlp.iter('node'):
		dtags = get_tags(n)
		nodes.load_xml_node(n,dtags)
def load_parcelles(fnparcelles):
	print('mise en cache des parcelles...')
	print('nodes...')
	sys.stdout.flush()
	xmlparcelles = ET.parse(fnparcelles)
	load_nodes_from_xml_parse(xmlparcelles)
	print('parcelles...')
	sys.stdout.flush()
	load_ways_from_xml_parse(xmlparcelles,'parcelle')
	del xmlparcelles
	gc.collect()

	print('chargement...')
	sys.stdout.flush()
	cur_parcelles = pgc.cursor()
	str_query = ""
	for idx,id in enumerate(ways.w['parcelle']):
		str_query = str_query+ways.w['parcelle'][id].get_as_SQL_import_parcelle()
		if idx%100 == 0:
			cur_parcelles.execute(str_query+"COMMIT;")
			str_query = ""
	if str_query != "":
		cur_parcelles.execute(str_query+"COMMIT;")
def load_ways_from_xml_parse(xmlp,osm_key):
	for b in xmlp.iter('way'):
		a_n = []
		for bn in b.iter('nd'):
			a_n.append(bn.get('ref'))
		g = WayGeom(a_n)
		dtags = get_tags(b)
		ways.add_way(Way(g,dtags,b.attrib,osm_key),b.get('id'),osm_key)
def normalize(s):

	return s
def main(args):
	debut_total = time.time()
	usage = 'USAGE : python parcelles_par_noms.py <code INSEE>'
	if len(args) != 2:
		print(usage)
		os._exit(0)

	global pgc,dicts,source,code_insee
	pgc = get_pgc()
	source = 'CADASTRE'
	code_insee = args[1]
	# code_cadastre = get_code_cadastre_from_insee(code_insee)
	code_cadastre = '61086' #KL326' #'W1172'
	code_cadastre = 'KL326' #'W1172'
	code_cadastre = 'W1172'
	code_cadastre = 'W1280'
	# code_dept = get_cadastre_code_dept_from_insee(code_insee)
	code_dept = '007'
	code_dept = '050'
	code_dept = '085'
	
	# batch_id = batch_start_log(source,'agregParcellesNommees',code_cadastre)

	global nodes,ways
	nodes = Nodes()
	ways = Ways()

	# fnparcelles = os.path.join('/data/work/cadastre.openstreetmap.fr/bano_cache',code_dept,code_cadastre,code_cadastre+'-parcelles.osm')
	fnparcelles = os.path.join('C:\\Users\\vincent\\Documents\\GitHub',code_cadastre+'-parcelles.osm')
	executeSQL_INSEE('sql/create_table_parcelles_insee.sql',code_insee)
	load_parcelles(fnparcelles)
	executeSQL_INSEE('sql/agrege_parcelles_par_nom_insee.sql',code_insee)
	# batch_end_log(nb_rec,batch_id)

	# print(adds)
	# if len(sel)>0:
		# for k in sel:
			# print(k,sel[k]['nombre'])
			# print(sel[k]['liste'])
	# print (freq)
	# geom_by_name()
	# load_geom_2_db()
	
if __name__ == '__main__':
    main(sys.argv)
