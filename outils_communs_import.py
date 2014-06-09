#!/usr/bin/env python
# coding: UTF-8

import psycopg2
import os.path
from pg_connexion import get_pgc
from pg_connexion import get_pgc_layers

class Dicts:
	def __init__(self):
		self.lettre_a_lettre = {}
		self.fantoir = {}
		self.code_fantoir_vers_nom_fantoir = {}
		self.osm_insee = {}
		self.abrev_type_voie = {}
		self.expand_titres = {}
		self.abrev_titres = {}
		self.chiffres = []
		self.chiffres_romains = []
		self.mot_a_blanc = []
		self.abrev_titres = {}
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
			# self.add_voie('fantoir',cle)
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
		self.expand_titres = [['CPT','CAPITAINE'],
							['GEN','GENERAL']]
	def load_abrev_titres(self):
		self.abrev_titres = [['MARECHAL','MAL'],
							['PRESIDENT','PDT'],
							['GENERAL','GAL'],
							['COMMANDANT','CDT'],
							['CAPITAINE','CAP'],
							['LIEUTENANT','LT'],
							['REGIMENT','REGT'],
							['PROFESSEUR','PROF'],
                            ['JEAN-BAPTISTE','J BTE'],
							['SAINTE','STE'],
							['SAINT','ST']]
	def load_chiffres_romains(self):
		self.chiffres_romains = {	'XXIII':'DEUXTROIS',
									'XXII' :'DEUXDEUX',
									'XXI'  :'DEUXUN',
									'XX'   :'DEUXZERO',
									'XIX'  :'UNNEUF',
									'XVIII':'UNHUIT',
									'XVII' :'UNSEPT',
									'XVI'  :'UNSIX',
									'XV'   :'UNCINQ',
									'XIV'  :'UNQUATRE',
									'XIII' :'UNTROIS',
									'XII'  :'UNDEUX',
									'XI'   :'UNUN',
									'X'    :'UNZERO',
									'IX'   :'NEUF',
									'VIII' :'HUIT',
									'VII'  :'SEPT',
									'VI'   :'SIX',
									'V'    :'CINQ',
									'IV'   :'QUATRE',
									'III'  :'TROIS',
									'II'   :'DEUX',
									'I'    :'UN'}
	def load_abrev_type_voie(self):
		fn = os.path.join(os.path.dirname(__file__), 'abrev_type_voie.txt')
		f = open(fn)
		for l in f:
			c = (l.splitlines()[0]).split('\t')
			self.abrev_type_voie[c[0]] = c[1]
		f.close()
	def load_osm_insee(self):
		finsee_path = os.path.join(os.path.dirname(__file__),'osm_id_ref_insee.csv')
		finsee = open(finsee_path,'r')
		for e in finsee:
			c = (e.splitlines()[0]).split(',')
			self.osm_insee[str(c[1])] = int(c[0])
		finsee.close()
	def load_all(self,code_insee_commune):
		self.load_lettre_a_lettre()
		self.load_abrev_type_voie()
		self.load_expand_titres()
		self.load_abrev_titres()
		self.load_chiffres()
		self.load_chiffres_romains()
		self.load_mot_a_blanc()
		self.load_osm_insee()
		self.load_fantoir(code_insee_commune)
	def add_voie(self,origine,nom):
		cle = normalize(nom)
		if not cle in self.noms_voies:
			self.noms_voies[cle] = {}
		self.noms_voies[cle][origine] = nom
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
def get_part_debut(s,nb_parts):
	resp = ''
	if get_nb_parts(s) > nb_parts:
		resp = ' '.join(s.split()[0:nb_parts])
	return resp
def get_nb_parts(s):
	return len(s.split())
def replace_type_voie(s,nb):
	sp = s.split()
	spd = ' '.join(sp[0:nb])
	spf = ' '.join(sp[nb:len(sp)])
	s = dicts.abrev_type_voie[spd]+' '+spf
	return s
def is_valid_housenumber(hsnr):
	is_valid = True
	if len(hsnr.encode('utf8')) > 10:
		is_valid = False
	return is_valid
def normalize(s):
	# print(s)
	# s = s.encode('ascii','ignore')
	s = s.upper()				# tout en majuscules
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
	p = 0
	while (not abrev_trouvee) and p < 3:
		p+= 1
		if get_part_debut(s,p) in dicts.abrev_type_voie:
			s = replace_type_voie(s,p)
			abrev_trouvee = True

	# ordinal
	s = s.replace(' EME ','EME ')

	# chiffres
	for c in dicts.chiffres:
		s = s.replace(c[0],c[1])

	# articles
	for c in dicts.mot_a_blanc:
		s = s.replace(' '+c+' ',' ')

	# titres, etc.
	for r in dicts.abrev_titres:
		s = s.replace(' '+r[0]+' ',' '+r[1]+' ')

	# chiffres romains
	sp = s.split()

	if sp[-1] in dicts.chiffres_romains:
		sp[-1] = dicts.chiffres_romains[sp[-1]]
		s = ' '.join(sp)
			
	return s
def add_fantoir_to_hsnr():
	for v in adresses.a:
		if v in dicts.fantoir:
			adresses.a[v]['fantoirs']['FANTOIR'] = dicts.fantoir[v]
			adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[dicts.fantoir[v]]
		else:
			if 'OSM' in adresses.a[v]['fantoirs']:
				adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[adresses.a[v]['fantoirs']['OSM']]
def get_data_from_pg(data_type,insee):
	fq = open('sql/{:s}.sql'.format(data_type),'rb')
	str_query = fq.read().replace('__com__',insee)
	fq.close()
	# print(str_query)
	# pgcl = get_pgcl()
	cur = pgcl.cursor()
	cur.execute(str_query)
	res = cur.fetchall()
	cur.close()
	return res
def load_highways_from_pg_osm(insee):
	data = get_data_from_pg('highway_insee',insee)
	for lt in data:
		l = list(lt)
		name = l[0].decode('utf8')
		cle = normalize(name)
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
		adresses.register(name)
		adresses.add_voie(name,'OSM')
def get_code_cadastre_from_insee(insee):
	str_query = 'SELECT cadastre_com FROM code_cadastre WHERE insee_com = \'{:s}\';'.format(insee)
	pgc = get_pgc()
	cur = pgc.cursor()
	cur.execute(str_query)
	for c in cur:
		code_cadastre = c[0]
	return code_cadastre
def	load_to_db(adresses,code_insee,source,code_cadastre,code_dept):
	sload = 'DELETE FROM cumul_adresses_dev WHERE insee_com = \'{:s}\' AND source = \'{:s}\';\n'.format(code_insee,source)
	cur_insert = pgc.cursor()
	cur_insert.execute(sload)
	nb_rec = 0
	for v in adresses.a:
		print(v)
		print(adresses.a[v])
		sload = 'INSERT INTO cumul_adresses_dev (geometrie,numero,voie_cadastre,voie_osm,fantoir,insee_com,cadastre_com,dept,code_postal,source) VALUES'
		a_values = []
		if not adresses.a[v]['numeros']:
			continue
		# street_name = v.title().encode('utf8')
		street_name_cadastre = ''
		street_name_osm = ''
		street_name_fantoir = ''
		cle_fantoir = get_best_fantoir(v)
		if 'OSM' in adresses.a[v]['voies']:
			street_name_osm =  adresses.a[v]['voies']['OSM'].encode('utf8')
		if 'FANTOIR' in adresses.a[v]['voies']:
			street_name_fantoir =  adresses.a[v]['voies']['FANTOIR'].encode('utf8')
		if 'CADASTRE' in adresses.a[v]['voies']:
			street_name_fantoir =  adresses.a[v]['voies']['CADASTRE'].encode('utf8')
		if street_name_osm == '' and street_name_fantoir == '':
			print('****** voies muettes '+v)
	# nodes
		for num in adresses.a[v]['numeros']:
			numadresse = adresses.a[v]['numeros'][num]
			a_values.append('(ST_PointFromText(\'POINT({:s} {:s})\', 4326),\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\',\'{:s}\')'.format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.encode('utf8'),street_name_fantoir.replace("'","''"),street_name_osm.replace("'","''"),cle_fantoir,code_insee,code_cadastre,code_dept,'',source))
			nb_rec +=1
		sload = sload+','.join(a_values)+';COMMIT;'
		cur_insert.execute(sload)
	return(nb_rec)
def get_best_fantoir(cle):
	res = ''
	if 'FANTOIR' in adresses.a[cle]['fantoirs']:
		res = adresses.a[cle]['fantoirs']['FANTOIR']
	if 'OSM' in adresses.a[cle]['fantoirs']:
		res = adresses.a[cle]['fantoirs']['OSM']
	return res
global pgc,pgcl
pgc = get_pgc()
pgcl = get_pgc_layers()

# global dicts
# dicts = Dicts()
# dicts.load_all(code_insee)
global adresses
adresses = Adresses()