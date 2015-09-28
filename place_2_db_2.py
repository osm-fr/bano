#!/usr/bin/env python
# coding: UTF-8
import sys
import time
import gc
import glob
import os,os.path
from pg_connexion import get_pgc
from pg_connexion import get_pgc_layers
from addr_2_db import get_code_cadastre_from_insee
from addr_2_db import get_cadastre_code_dept_from_insee
# from addr_2_db import normalize
from addr_2_db import get_cache_filename	
from addr_2_db import get_tags
from addr_2_db import get_part_debut
from addr_2_db import replace_type_voie
# from addr_2_db import Dicts
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import xml.etree.ElementTree as ET

class Dicts:
	def __init__(self):
		self.lettre_a_lettre = {}
		# self.code_fantoir_vers_noms = {}
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
						'U':[u'Û',u'Ü'],
						'OE':[u'Œ']}
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
			if l[0:1] == '#':
				continue
			c = (l.splitlines()[0]).split('\t')
			self.expand_titres.append(c)
		f.close()
	def load_expand_noms(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','expand_noms.txt')
		f = open(fn)
		for l in f:
			if l[0:1] == '#':
				continue
			c = (l.splitlines()[0]).split('\t')
			self.expand_noms.append(c)
		f.close()
	def load_abrev_titres(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_titres.txt')
		f = open(fn)
		for l in f:
			if l[0:1] == '#':
				continue
			c = (l.splitlines()[0]).split('\t')
			self.abrev_titres.append(c)
		f.close()
	def load_chiffres_romains(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','chiffres_romains.txt')
		f = open(fn)
		for l in f:
			if l[0:1] == '#':
				continue
			c = (l.splitlines()[0]).split('\t')
			self.chiffres_romains[c[0]] = c[1]
		f.close()
	def load_abrev_type_voie(self):
		fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_type_voie.txt')
		f = open(fn)
		for l in f:
			if l[0:1] == '#':
				continue
			c = (l.splitlines()[0]).split('\t')
			self.abrev_type_voie[c[0]] = c[1]
		f.close()
	def load_all(self):
		self.load_lettre_a_lettre()
		self.load_abrev_type_voie()
		self.load_expand_noms()
		self.load_expand_titres()
		self.load_abrev_titres()
		self.load_chiffres()
		self.load_chiffres_romains()
		self.load_mot_a_blanc()
		# self.load_fantoir(code_insee_commune)

class Place:
	def __init__(self,lon,lat,place,name,bati,source,fantoir):
		self.lon = lon
		self.lat = lat
		self.place = place
		self.name = name
		self.bati = bati
		self.source = source
		self.fantoir = fantoir
		
		if self.source == 'CADASTRE':
			self.name = format_toponyme(self.name)
		if not self.fantoir or self.fantoir == '':
			self.fantoir = match_fantoir(self.name)
		if source == 'OSM' and self.place != 'locality':
			self.bati = '1'
			
	def get_geom_as_text(self):
		strp = 'ST_PointFromText(\'POINT('+str(self.lon)+' '+str(self.lat)+')\',4326)'
		return strp
	def get_value_as_insert_for_cumul_places(self):
# geometrie libelle_cadastre libelle_osm libelle_fantoir fantoir insee_com cadastre_com dept code_postal source batch_import_id ld_bati ld_osm
		return "({:s},'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}')".format(self.get_geom_as_text(),self.name.encode('utf8').replace('\'','\'\''),self.fantoir,self.place,self.bati,code_insee,code_cadastre,code_dept,'',source)
def format_toponyme(s):
	a_s = s.replace('\'',' ').split(' ')
	
	# a_s = s.split('\'')
	# a_s = [a[0:-1]+a[-1].lower() for a in a_s]
	
	# Accents
	dic_replace_accents = {}
	dic_replace_accents['DERRIERE'] = u'DERRIÈRE'
	dic_replace_accents['EGLISE'] = u'ÉGLISE'
	dic_replace_accents['ILE'] = u'ÎLE'
	dic_replace_accents['ILOT'] = u'ÎLOT'
	dic_replace_accents['PRE'] = u'PRÉ'

	for m in range(0,len(a_s)):
		if a_s[m] in dic_replace_accents:
			a_s[m] = dic_replace_accents[a_s[m]]
	
	# Capitalisation
	a_s = [a.capitalize() for a in a_s]

	# Minuscules
	dic_replace_hors_premier_mot = {}
	dic_replace_hors_premier_mot['Au'] = 'au'
	dic_replace_hors_premier_mot['Aux'] = 'aux'
	dic_replace_hors_premier_mot['D'] = 'd\''
	dic_replace_hors_premier_mot['De'] = 'de'
	dic_replace_hors_premier_mot['Des'] = 'des'
	dic_replace_hors_premier_mot['Du'] = 'du'
	dic_replace_hors_premier_mot['Et'] = 'et'
	dic_replace_hors_premier_mot['L'] = 'l\''
	dic_replace_hors_premier_mot['La'] = 'la'
	dic_replace_hors_premier_mot['Le'] = 'le'
	dic_replace_hors_premier_mot['Les'] = 'les'
	dic_replace_hors_premier_mot['Un'] = 'un'
	dic_replace_hors_premier_mot['Une'] = 'une'
	
	if len(a_s) > 1:
		for m in range(1,len(a_s)):
			if a_s[m] in dic_replace_hors_premier_mot:
				a_s[m] = dic_replace_hors_premier_mot[a_s[m]]
	
	# Appostrophes
	dic_ajoute_apostrophe = {}
	dic_ajoute_apostrophe['d'] = 'd\''
	dic_ajoute_apostrophe['D'] = 'D\''
	dic_ajoute_apostrophe['l'] = 'l\''
	dic_ajoute_apostrophe['L'] = 'L\''

	for m in range(0,len(a_s)):
		if a_s[m] in dic_ajoute_apostrophe:
			a_s[m] = dic_ajoute_apostrophe[a_s[m]]
	
	s = ' '.join(a_s).replace('\' ','\'\'')
	if s.strip()[-1] == '\'':
		s = s.strip()[0:-1]
	return s
def	executeSQL_INSEE(fnsql,code_insee):
	fsql = open(fnsql,'rb')
	str_query = fsql.read()
	fsql.close()
	str_query = str_query.replace('__com__','_'+code_insee)
	str_query = str_query.replace('#com__',code_insee)
	cur_sql = pgc.cursor()
	cur_sql.execute(str_query)
	cur_sql.close()
def get_data_from_pg(data_type,insee_com):
	fq = open('sql/{:s}.sql'.format(data_type),'rb')
	str_query = fq.read().replace('#com__',insee_com)
	fq.close()
	cur = pgc.cursor()
	cur.execute(str_query)
	res = []
	# f = open(cache_file,'w+')
	res = [list(lt) for lt in cur]
	# print(res)
	# os._exit(0)
	return res
def get_data_from_pgl(data_type,insee_com,cadastre_com):
	cache_file = get_cache_filename(data_type,insee_com,cadastre_com)
	if not os.path.exists(cache_file) or (time.time() - os.path.getmtime(cache_file)) > 86400 :
		fq = open('sql/{:s}.sql'.format(data_type),'rb')
		str_query = fq.read().replace('__com__',insee_com)
		fq.close()
		cur = pgcl.cursor()
		cur.execute(str_query)
		f = open(cache_file,'w+')
		for lt in cur:
			l = list(lt)
			f.write(str(l)+'\n')
		cur.close()
		f.seek(0)
	else :
		f = open(cache_file,'r')
	res = []
	for l in f:
		res.append(eval(l))
	f.close()
	return res
def load_fantoir(insee):
	str_query = '''	SELECT 	code_insee||id_voie||cle_rivoli,
							nature_voie||' '||libelle_voie
					FROM	fantoir_voie
					WHERE	code_insee = \''''+insee+'''\' AND
							type_voie = \'3\' AND
							caractere_annul = \'\';'''
	cur_fantoir = pgc.cursor()
	cur_fantoir.execute(str_query)
	for c in cur_fantoir:
		cle = ' '.join(c[1].replace('-',' ').split())
		cle = normalize(cle)
		fantoir[cle] = c[0]
def load_to_db(data,code_insee,source,code_cadastre,code_dept):
	table_dest = 'cumul_places'
	sload = 'DELETE FROM {:s} WHERE insee_com = \'{:s}\' AND source = \'{:s}\';\n'.format(table_dest,code_insee,source)
	cur_insert = pgc.cursor()
	cur_insert.execute(sload)
	nb_rec = 0
	sload = 'INSERT INTO {:s} (geometrie,libelle_{:s},fantoir,ld_osm,ld_bati,insee_com,cadastre_com,dept,code_postal,source) VALUES'.format(table_dest,source.lower())
	a_values = []
	for p in data:
		# print(p.get_value_as_insert_for_cumul_places())
		# os._exit(0)
		a_values.append(p.get_value_as_insert_for_cumul_places())
		nb_rec +=1
	sload = sload+','.join(a_values)+';COMMIT;'
	# print(sload)
	if nb_rec>0:
		cur_insert.execute(sload)
	return(nb_rec)
def match_fantoir(name):
	res = ''
	name_norm = normalize(name)
	# print(name_norm)
	if name_norm in fantoir:
		res = fantoir[name_norm]
	return res
def normalize(s):
	# if s[0:2] == 'BD' or s[0:4] == 'Boul':
	# print(s)
	s = s.upper()				# tout en majuscules
	s = s.split(' (')[0]		# parenthèses : on coupe avant
	s = s.replace('-',' ')		# separateur espace
	s = s.replace('\'',' ')		# separateur espace
	s = s.replace('’'.decode('utf8'),' ')		# separateur espace
	s = s.replace('/',' ')		# separateur espace
	s = s.replace(':',' ')		# separateur deux points
	s = ' '.join(s.split())		# separateur : 1 espace
	# print(s)
	for l in iter(dicts.lettre_a_lettre):
		for ll in dicts.lettre_a_lettre[l]:
			s = s.replace(ll,l)
	s = s.encode('ascii','ignore')
	
# type de voie
	# abrev_trouvee = False
	# p = 5
	# while (not abrev_trouvee) and p > -1:
		# p-= 1
		# if get_part_debut(s,p) in dicts.abrev_type_voie:
			# s = replace_type_voie(s,p)
			# abrev_trouvee = True
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
	return s

def main(args):
	debut_total = time.time()
	usage = 'USAGE : python place_2_db.py <code INSEE> <CADASTRE|OSM>'
	if len(args) < 3:
		print(usage)
		os._exit(0)

	global pgc,pgcl,fantoir,source,code_insee,code_cadastre,code_dept,dicts
	source = args[2].upper()
	if source not in ['OSM','CADASTRE']:
		print(usage)
		os._exit(0)

	pgc = get_pgc()
	pgcl = get_pgc_layers()
	code_insee = args[1]
	code_cadastre = get_code_cadastre_from_insee(code_insee)
	code_dept = get_cadastre_code_dept_from_insee(code_insee)
	fantoir = {}
	dicts = Dicts()
	dicts.load_all()
	load_fantoir(code_insee)
	# print(dicts)
	batch_id = batch_start_log(source,'cumulPlaces',code_cadastre)

	global places
	places = []
	if source == 'CADASTRE':
		data = get_data_from_pg('cadastre_2_places',code_insee)
		# for d in data:
			# places.append(Place(d[0],d[1],d[2],d[3],d[5],source,d[4]))
	else:
		data = get_data_from_pgl('place_insee',code_insee,code_cadastre)
	for d in data:
		places.append(Place(d[0],d[1],d[2],d[3].decode('utf8'),d[5],source,d[4]))
		
	nb_rec = load_to_db(places,code_insee,source,code_cadastre,code_dept)
	batch_end_log(nb_rec,batch_id)

if __name__ == '__main__':
    main(sys.argv)
