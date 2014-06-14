#!/usr/bin/env python
# coding: UTF-8
import copy
import glob
import gc
import urllib,urllib2
import sys
import shutil
import os,os.path
import psycopg2
from pg_connexion import get_pgc
from pg_connexion import get_pgc_layers
import socket
import time 
import xml.etree.ElementTree as ET
import xml.sax.saxutils as XSS
import zipfile
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
from outils_communs_import import get_part_debut
from outils_communs_import import get_data_from_pg
from outils_communs_import import get_code_cadastre_from_insee
from outils_communs_import import load_to_db
from outils_communs_import import is_valid_housenumber

debut_total = time.time()

class Dicts:
	def __init__(self):
		self.lettre_a_lettre = {}
		self.fantoir = {}
		self.code_fantoir_vers_nom_fantoir = {}
		self.code_fantoir_vers_noms = {}
		self.osm_insee = {}
		self.abrev_type_voie = {}
		self.expand_noms = []
		self.expand_titres = []
		self.abrev_titres = []
		self.chiffres = []
		self.chiffres_romains = {}
		self.mot_a_blanc = []
		self.noms_voies = {}
		self.ways_osm = {}

	def load_lettre_a_lettre(self):
		self.lettre_a_lettre = {'A':[u'Â',u'À'],
						'C':[u'Ç'],
						'E':[u'È',u'Ê',u'É',u'Ë'],
						'I':[u'Ï',u'Î'],
						'O':[u'Ö',u'Ô'],
						'U':[u'Û',u'Ü']}
	def load_fantoir(self,insee):
		str_query = '''	SELECT 	code_insee||id_voie||cle_rivoli,
								nature_voie||' '||libelle_voie
						FROM	fantoir_voie
						WHERE	code_insee = \''''+insee+'''\' AND
								caractere_annul NOT IN ('O','Q');'''
		cur_fantoir = pgc.cursor()
		cur_fantoir.execute(str_query)
		for c in cur_fantoir:
			self.code_fantoir_vers_nom_fantoir[c[0]] = c[1]
			cle = ' '.join(c[1].replace('-',' ').split())
			cle = normalize(cle)
			self.fantoir[cle] = c[0]
	def load_addr_from_fantoir(self):
		for k in self.fantoir:
			adresses.add_fantoir(k,self.fantoir[k],'FANTOIR')
	def load_chiffres(self):
		self.chiffres = [	['0','ZERO'],
							['1','UN'],
							['2','DEUX'],
							['3','TROIS'],
							['4','QUATRE'],
							['5','CINQ'],
							['6','SIX'],
							['7','SEPT'],
							['8','HUIT'],
							['9','NEUF'],
							[' DIX ',' UNZERO '],
							[' ONZE ',' UNUN '],
							[' DOUZE ',' UNDEUX '],
							[' TREIZE ',' UNTROIS '],
							[' QUATORZE ',' UNQUATRE ']]
	def load_mot_a_blanc(self):
		self.mot_a_blanc = ['DE LA',
							'DU',
							'DES',
							'LE',
							'LA',
							'LES',
							'DE',
							'D']
	def load_expand_titres(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','expand_titres.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.expand_titres.append(c)
		f.close()
	def load_expand_noms(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','expand_noms.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.expand_noms.append(c)
		f.close()
	def load_abrev_titres(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_titres.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.abrev_titres.append(c)
		f.close()
	def load_chiffres_romains(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','chiffres_romains.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.chiffres_romains[c[0]] = c[1]
		f.close()
	def load_abrev_type_voie(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_type_voie.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.abrev_type_voie[c[0]] = c[1]
		f.close()
	# def load_osm_insee(self):
		# finsee_path = os.path.join(os.path.dirname(__file__),'osm_id_ref_insee.csv')
		# finsee = open(finsee_path,'r')
		# for e in finsee:
			# c = (e.splitlines()[0]).split(',')
			# self.osm_insee[str(c[1])] = int(c[0])
		# finsee.close()
	def load_all(self,code_insee_commune):
		self.load_lettre_a_lettre()
		self.load_abrev_type_voie()
		self.load_expand_noms()
		self.load_expand_titres()
		self.load_abrev_titres()
		self.load_chiffres()
		self.load_chiffres_romains()
		self.load_mot_a_blanc()
		# self.load_osm_insee()
		self.load_fantoir(code_insee_commune)
	def add_voie(self,origine,nom):
		cle = normalize(nom)
		if not cle in self.noms_voies:
			self.noms_voies[cle] = {}
		self.noms_voies[cle][origine] = nom
	def add_fantoir_name(self,fantoir,name,source):
		if not fantoir in self.code_fantoir_vers_noms:
			self.code_fantoir_vers_noms[fantoir] = {}
		if not source in self.code_fantoir_vers_noms[fantoir]:
			self.code_fantoir_vers_noms[fantoir][source] = name
	def get_fantoir_name(self,fantoir,source):
		res = ''
		if fantoir in self.code_fantoir_vers_noms:
			if source in self.code_fantoir_vers_noms[fantoir]:
				res = self.code_fantoir_vers_noms[fantoir][source]
		return res
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
#		if id == '535300376':
#			os._exit(0)
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
			if 'addr:street' in tmp_addrs[sa] and 'addr:housenumber' in tmp_addrs[sa]:
				self.addrs[sa] = tmp_addrs[sa]
				dicts.add_voie('parcelle',tmp_addrs[sa]['addr:street'])
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
		str_query = ""
		for a in self.addrs:
			str_query = str_query+'''INSERT INTO parcelles_'''+code_insee+''' 
							(SELECT ST_Transform(ST_SetSRID(ST_MakePolygon(ST_GeomFromText('''+(self.geom.get_geom_as_linestring_text())+''')),4326),2154),
							'''+self.attrib['id']+''',\''''+self.addrs[a]['addr:housenumber']+'''\',\''''+normalize(self.addrs[a]['addr:street'])+'''\');'''
		return str_query
class Ways:
	def __init__(self):
		self.w = {'highway':{},
				'building':{},
				'parcelle':{},
				'centroid_building':{}}
	def add_way(self,w,id,osm_key):
		self.w[osm_key][id] = w
class Adresse:
	def __init__(self,node,num,voie,fantoir):
		self.node = node
		self.numero = num
		self.voie = voie
		self.fantoir = fantoir
class Adresses:
	def __init__(self):
		self.a = {}
	def register(self,voie):
		cle = normalize(voie)
		# print(cle+' '+voie)
		if not cle in self.a:
			self.a[cle] = {'numeros':{},'voies':{},'fantoirs':{}}
	def add_fantoir(self,cle,fantoir,source):
		self.register(cle)
		if len(fantoir) == 10:
			self.a[cle]['fantoirs'][source] = fantoir
		else:
			print(u'Code Fantoir non conforme : {:s}'.format(fantoir))
	def add_voie(self,voie,source):
		cle = normalize(voie)
		self.a[cle]['voies'][source] = voie
	def add_adresse(self,ad,source):
		""" une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
		if (ad.fantoir == '' or (is_valid_fantoir(ad.fantoir) and ad.fantoir[0:5] == code_insee)) and is_valid_housenumber(ad.numero):
			cle = normalize(ad.voie)
			self.add_voie(ad.voie,source)
			self.a[cle]['numeros'][ad.numero] = ad
			if ad.fantoir != '':
				self.a[cle]['fantoirs']['OSM'] = ad.fantoir
		else:
			print(u'adresse rejetée : {:s} {:s}'.format(ad.numero,ad.fantoir))
	def get_cle_by_fantoir(self,fantoir):
		cle = ''
		for c in self.a:
			if 'fantoirs' in self.a[c]:
				if 'OSM' in self.a[c]['fantoirs']:
					if self.a[c]['fantoirs']['OSM'] == fantoir:
						cle = c
						break
				if 'FANTOIR' in self.a[c]['fantoirs']:
					if self.a[c]['fantoirs']['FANTOIR'] == fantoir:
						cle = c
						break
		return cle
	def has_already_fantoir(self,cle,source):
		has = False
		if source in self.a[cle]['fantoirs']:
			has = True
		return has
def normalize(s):
	# if s[0:2] == 'BD' or s[0:4] == 'Boul':
		# print(s)
	s = s.upper()				# tout en majuscules
	s = s.split(' (')[0]		# parenthèses : on coupe avant
	s = s.replace('-',' ')		# separateur espace
	s = s.replace('\'',' ')		# separateur espace
	s = s.replace('/',' ')		# separateur espace
	s = s.replace(':',' ')		# separateur deux points
	s = ' '.join(s.split())		# separateur : 1 espace
	for l in iter(dicts.lettre_a_lettre):
		for ll in dicts.lettre_a_lettre[l]:
			s = s.replace(ll,l)
	s = s.encode('ascii','ignore')
	
	# type de voie
	abrev_trouvee = False
	p = 5
	while (not abrev_trouvee) and p > -1:
		p-= 1
		if get_part_debut(s,p) in dicts.abrev_type_voie:
			s = replace_type_voie(s,p)
			abrev_trouvee = True
	# ordinal
	s = s.replace(' EME ','EME ')
	s = s.replace(' 1ER ',' PREMIER ')

	# chiffres
	for c in dicts.chiffres:
		s = s.replace(c[0],c[1])

	# titres, etc.
	for r in dicts.expand_noms:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
		if s[-len(r[0]):] == r[0]:
			s = s.replace(' '+r[0],' '+r[1])
	for r in dicts.expand_titres:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
	for r in dicts.abrev_titres:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')

	# articles
	for c in dicts.mot_a_blanc:
		s = s.replace(' '+c+' ',' ')

	# chiffres romains
	sp = s.split()

	if sp[-1] in dicts.chiffres_romains:
		sp[-1] = dicts.chiffres_romains[sp[-1]]
		s = ' '.join(sp)
	# if s[0:2] == 'BD' or s[0:4] == 'Boul':
		# print(s)
	return s
def replace_type_voie(s,nb):
	sp = s.split()
	spd = ' '.join(sp[0:nb])
	spf = ' '.join(sp[nb:len(sp)])
	s = dicts.abrev_type_voie[spd]+' '+spf
	return s
def load_highways_from_pg_osm(insee):
	data = get_data_from_pg('highway_insee',insee)
	for lt in data:
		l = list(lt)
		name = l[0].decode('utf8')
		if len(name) < 2:
			continue
		adresses.register(name)
		cle = normalize(name)
		if adresses.has_already_fantoir(cle,'OSM'):
			# print(cle)
			# print(l)
			continue
		fantoir = ''
		if len(l)>1:
			if l[1] != None and l[1][0:5] == insee:
				fantoir = l[1]
				adresses.add_fantoir(cle,l[1],'OSM')
		if len(l)>2 and fantoir == '':
			if l[2] != None and l[2][0:5] == insee:
				fantoir = l[2]
				adresses.add_fantoir(cle,l[2],'OSM')
		if len(l)>3 and fantoir == '':
			if l[3] != None and l[3][0:5] == insee:
				fantoir = l[3]
				adresses.add_fantoir(cle,l[3],'OSM')
		if fantoir != '':
			dicts.add_fantoir_name(fantoir,name,'OSM')
		adresses.add_voie(name,'OSM')
def load_highways_relations_from_pg_osm(insee):
	data = get_data_from_pg('highway_relation_insee',insee)
	for lt in data:
		l = list(lt)
		name = l[0].decode('utf8')
		if len(name) < 2:
			continue
		adresses.register(name)
		cle = normalize(name)
		if adresses.has_already_fantoir(cle,'OSM'):
			# print(cle)
			# print(l)
			continue
		fantoir = ''
		tags = tags_list_as_dict(l[1])
		if 'ref:FR:FANTOIR' in tags:
			if tags['ref:FR:FANTOIR'][0:5] == code_insee and len(tags['ref:FR:FANTOIR']) == 10:
				fantoir = tags['ref:FR:FANTOIR']
		if fantoir != '':
			dicts.add_fantoir_name(fantoir,name,'OSM')
		adresses.add_voie(name,'OSM')
def	load_hsnr_from_cad_file(fnadresses,source):
	xmladresses = ET.parse(fnadresses)
	dict_node_relations = {}
	for asso in xmladresses.iter('relation'):
		dtags = get_tags(asso)
		if not 'type' in dtags:
			continue
		if dtags['type'] != 'associatedStreet':
			continue
		if not 'name' in dtags:
			continue
		if len(dtags['name']) < 2:
			continue
		# if 'ref:FR:FANTOIR' in dtags:
			# adresses.add_fantoir(normalize(dtags['name']),dtags['ref:FR:FANTOIR'],source)
		adresses.register(dtags['name'])
		adresses.add_voie(dtags['name'],'CADASTRE')
		for n in asso.iter('member'):
			if n.get('type') == 'node':
				if not n.get('ref') in dict_node_relations:
					dict_node_relations[n.get('ref')] = []
					# print(dtags['name'])
					# print(normalize(dtags['name']))
				dict_node_relations[n.get('ref')].append(normalize(dtags['name']))
	for n in xmladresses.iter('node'):
		dtags = get_tags(n)
		n_id = n.get('id')
		if 'addr:housenumber' in dtags and n_id in dict_node_relations:
			if is_valid_housenumber(dtags['addr:housenumber']):
				for v in dict_node_relations[n_id]:
					nd = Node({'id':n_id,'lon':n.get('lon'),'lat':n.get('lat')},{})
					adresses.add_adresse(Adresse(nd,dtags['addr:housenumber'],adresses.a[v]['voies']['CADASTRE'],''),source)
					# adresses.add_adresse(Adresse(nd,dtags['addr:housenumber'],v,''),source)
			else:
				print('Numero invalide : {:s}'.format(dtags['addr:housenumber'].encode('utf8')))
def tags_list_as_dict(ltags):
	res = {}
	for i in range(0,int(len(ltags)/2)):
		res[ltags[i*2]] = ltags[i*2+1]
	return res
def get_tags(xmlo):
	dtags = {}
	for tg in xmlo.iter('tag'):
		dtags[tg.get('k')] = tg.get('v')
	return dtags
def	load_to_db(adresses,code_insee,source,code_cadastre,code_dept):
	table_dest = 'cumul_adresses'
	sload = 'DELETE FROM {:s} WHERE insee_com = \'{:s}\' AND source = \'{:s}\';\n'.format(table_dest,code_insee,source)
	cur_insert = pgc.cursor()
	cur_insert.execute(sload)
	nb_rec = 0
	for v in adresses.a:
		# print(v)
		# print(adresses.a[v])
		sload = 'INSERT INTO {:s} (geometrie,numero,voie_cadastre,voie_osm,voie_fantoir,fantoir,insee_com,cadastre_com,dept,code_postal,source) VALUES'.format(table_dest)
		a_values = []
		if not adresses.a[v]['numeros']:
			continue
		street_name_cadastre = ''
		street_name_osm = ''
		street_name_fantoir = ''
		cle_fantoir = get_best_fantoir(v)
		if 'OSM' in adresses.a[v]['voies']:
			street_name_osm =  adresses.a[v]['voies']['OSM'].encode('utf8')
		else :
			street_name_osm = dicts.get_fantoir_name(cle_fantoir,'OSM').encode('utf8')
			# print(street_name_osm)
		if 'FANTOIR' in adresses.a[v]['voies']:
			street_name_fantoir =  adresses.a[v]['voies']['FANTOIR'].encode('utf8')
		if 'CADASTRE' in adresses.a[v]['voies']:
			street_name_cadastre =  adresses.a[v]['voies']['CADASTRE'].encode('utf8')
		if street_name_osm == '' and street_name_cadastre == '':
			print('****** voies muettes '+v)
	# nodes
		for num in adresses.a[v]['numeros']:
			numadresse = adresses.a[v]['numeros'][num]
			a_values.append('(ST_PointFromText(\'POINT({:s} {:s})\', 4326),\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\')'.format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.encode('utf8'),street_name_cadastre.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,code_insee,code_cadastre,code_dept,'',source))
			nb_rec +=1
		sload = sload+','.join(a_values)+';COMMIT;'
		cur_insert.execute(sload)
		# if v == 'RUE PREMIER BATAILLON CHASSEURS A PIEDS':
			# print(adresses.a[v]['voies'])
			# os._exit(0)
	# print(adresses.a['AV GUY MAUPASSANT'])
	# print(adresses.a['AV G MAUPASSANT CAP'])
	# print(dicts.expand_noms)
	return(nb_rec)
def add_fantoir_to_hsnr():
	for v in adresses.a:
		if v in dicts.fantoir:
			adresses.a[v]['fantoirs']['FANTOIR'] = dicts.fantoir[v]
			adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[dicts.fantoir[v]]
			# print(v)
			# print(adresses.a[v]['voies']['FANTOIR'])
			# if 'OSM' in adresses.a[v]['voies']:
				# print(adresses.a[v]['voies']['OSM'])
			# else:
				# print('***')
		else:
			if 'OSM' in adresses.a[v]['fantoirs']:
				if adresses.a[v]['fantoirs']['OSM'] in dicts.code_fantoir_vers_nom_fantoir:
					adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[adresses.a[v]['fantoirs']['OSM']]
def get_best_fantoir(cle):
	res = ''
	if 'FANTOIR' in adresses.a[cle]['fantoirs']:
		res = adresses.a[cle]['fantoirs']['FANTOIR']
	if 'OSM' in adresses.a[cle]['fantoirs']:
		res = adresses.a[cle]['fantoirs']['OSM']
	return res
def main(args):
	debut_total = time.time()
	if len(args) < 2:
		print('USAGE : python addr_cad_2_db.py <code INSEE>')
		os._exit(0)

	global source,batch_id
	global pgc,pgcl
	global code_insee,code_cadastre,code_dept
	global dicts
	global nodes,ways,adresses
	
	adresses = Adresses()
	source = 'CADASTRE'
	
	pgc = get_pgc()
	pgcl = get_pgc_layers()
	
	code_insee = args[1]
	code_cadastre = get_code_cadastre_from_insee(code_insee)
	code_dept = '0'+code_insee[0:2]
	if code_insee[0:2] == '97':
		code_dept = code_insee[0:3]
	
	batch_id = batch_start_log(source,'loadCumul',code_cadastre)
	
	dicts = Dicts()
	dicts.load_all(code_insee)
	rep_parcelles_adresses = '/data/work/cadastre.openstreetmap.fr/bano_cache/'+code_dept+'/'+code_cadastre
	fnadresses = rep_parcelles_adresses+'/'+code_cadastre+'-adresses.osm'
	load_hsnr_from_cad_file(fnadresses,source)
	load_highways_from_pg_osm(code_insee)
	load_highways_relations_from_pg_osm(code_insee)
	add_fantoir_to_hsnr()
	nb_rec = load_to_db(adresses,code_insee,source,code_cadastre,code_dept)
	
	batch_end_log(nb_rec,batch_id)
	fin_total = time.time()
	print('Execution en '+str(int(fin_total - debut_total))+' s.')
if __name__ == '__main__':
    main(sys.argv)

