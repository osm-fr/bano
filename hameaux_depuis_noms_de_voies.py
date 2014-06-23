#!/usr/bin/env python
# coding: UTF-8
import sys
import time
import os,os.path
from pg_connexion import get_pgc
from pg_connexion import get_pgc_layers
from addr_2_db import get_code_cadastre_from_insee
from addr_2_db import get_nb_parts
from addr_2_db import get_part_debut
from addr_2_db import get_tags
from addr_2_db import is_valid_housenumber
from addr_2_db import Node
from addr_2_db import Adresse
from addr_2_db import Adresses
import xml.etree.ElementTree as ET

class Adresses:
	def __init__(self):
		self.a = {}
	def register(self,voie):
		cle = normalize(voie)
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
def	load_hsnr_from_cad_file(fnadresses):
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
		adresses.register(dtags['name'])
		adresses.add_voie(dtags['name'],'CADASTRE')
		for n in asso.iter('member'):
			if n.get('type') == 'node':
				if not n.get('ref') in dict_node_relations:
					dict_node_relations[n.get('ref')] = []
				dict_node_relations[n.get('ref')].append(normalize(dtags['name']))
	for n in xmladresses.iter('node'):
		dtags = get_tags(n)
		n_id = n.get('id')
		if 'addr:housenumber' in dtags and n_id in dict_node_relations:
			if is_valid_housenumber(dtags['addr:housenumber']):
				for v in dict_node_relations[n_id]:
					nd = Node({'id':n_id,'lon':n.get('lon'),'lat':n.get('lat')},{})
					adresses.add_adresse(Adresse(nd,dtags['addr:housenumber'],adresses.a[v]['voies']['CADASTRE'],''),source)
			else:
				print('Numero invalide : {:s}'.format(dtags['addr:housenumber'].encode('utf8')))
# def geom_by_name():

def name_frequency():
	freq = {}
	for v in adresses.a:
		s = v.split()
		if len(s)>4:
			k = ' '.join(s[-2:])
			if k not in freq:
				freq[k] = {'nombre':1,'liste':[v]}
			else:
				freq[k]['nombre'] +=1
				freq[k]['liste'].append(v)
		if len(s)>3:
			k = v.split()[-1]
			if k not in freq:
				freq[k] = {'nombre':1,'liste':[v]}
			else:
				freq[k]['nombre'] +=1
				freq[k]['liste'].append(v)
	return freq
def	select_street_names_by_name(freq):
	sel = {}
	for k in freq:
		if freq[k]['nombre'] > 5:
			sel[k] = freq[k]
	return sel
def normalize(s):

	return s
def main(args):
	debut_total = time.time()
	usage = 'USAGE : python hameaux_depuis_noms_de_voies.py <code INSEE>'
	if len(args) != 2:
		print(usage)
		os._exit(0)

	pgc = get_pgc()
	global dicts,adresses,source
	source = 'CADASTRE'
	adresses = Adresses()
	code_insee = args[1]
	code_cadastre = get_code_cadastre_from_insee(code_insee)

	# fnadresses = os.path.join('/data/work/cadastre.openstreetmap.fr/bano_cache',code_dept,code_cadastre,code_cadastre+'-adresses.osm')
	fnadresses = os.path.join('C:\\Users\\vincent\\Documents\\GitHub',code_cadastre+'-adresses.osm')
	load_hsnr_from_cad_file(fnadresses)
	freq = name_frequency()
	sel = select_street_names_by_name(freq)
	if len(sel)>0:
		for k in sel:
			print(k,sel[k]['nombre'])
			print(sel[k]['liste'])
	# print (freq)
	# geom_by_name()
	# load_geom_2_db()
	
if __name__ == '__main__':
    main(sys.argv)
