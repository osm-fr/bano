#!/usr/bin/env python
# coding: UTF-8

# Place : ID = Fantoir quand présent, sinon nom normalisé
# 1- chargement Fantoir
# 2- chargement cadastre, rapprochement Fantoir, géométrie Cadastre calculée des parcelles
# 3- chargement OSM, rapprochement Fantoir, géométrie OSM
# 4- 

import sys
import time
import os
from pg_connexion import get_pgc,get_pgc_layers
from addr_2_db import get_cadastre_code_dept_from_insee,get_cache_filename
from outils_de_gestion import batch_start_log,batch_end_log,get_cadastre_format,get_cadastre_etape_timestamp_debut
# from outils_de_gestion import 

class Fantoir:
    def __init__(self,name,fantoir,bati):
        self.name = name
        self.name_norm = normalize(name)
        self.fantoir = fantoir
        self.bati = bati
class Cadastre:
    def __init__(self,lon,lat,name):
        self.lon = lon
        self.lat = lat
        self.name = name
        self.name_norm = normalize(name)
class Osm:
    def __init__(self,lon,lat,place,name,fantoir):
        self.lon = lon
        self.lat = lat
        self.place = place
        self.name = name
        self.name_norm = normalize(name)
        self.fantoir = fantoir
class Place:
    def __init__(self,lon,lat,place,name_fantoir,name_cadastre,name_osm,source,fantoir,bati):
        self.has_fantoir = False
        self.has_osm = False
        self.has_cadastre = False
        self.fantoir = Fantoir(name_fantoir,fantoir,bati)
        self.osm = Osm(lon,lat,place,name_osm,fantoir)
        self.cadastre = Cadastre(lon,lat,name_cadastre)
        if self.fantoir.name != '':
            self.has_fantoir = True
        if self.osm.name != '':
            self.has_osm = True
        if self.cadastre.name != '':
            self.has_cadastre = True
#        self.source = source
        self.id = self.fantoir.fantoir or (self.cadastre.name_norm or self.osm.name_norm)
    def update_fantoir(self,name,fantoir,bati):
        self.fantoir = Fantoir(name,fantoir,bati)
        self.has_fantoir = True
    def update_osm(self,lon,lat,place,name,fantoir=''):
        self.osm = Osm(lon,lat,place,name,fantoir)
        self.has_osm = True
    def update_cadastre(self,lon,lat,name):
        self.cadastre = Cadastre(lon,lat,name)
        self.has_cadastre = True
    def as_string(self):
        return "{:s}:{:s}\t{:s}\t{:6f}\t{:6f}\t{:s}\t{:s}\t{:6f}\t{:6f}\t{:s}".format(self.id,self.fantoir.name,self.fantoir.fantoir,self.osm.lon,self.osm.lat,self.osm.place,self.osm.name,self.cadastre.lon,self.cadastre.lat,self.cadastre.name)
    def as_SQL_cadastre_row(self):
        if self.has_cadastre:
            if self.has_osm and self.has_fantoir:
                return "(ST_PointFromText('POINT({:7f} {:7f})',4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','','{:s}',{:s},'')".format(self.cadastre.lon,self.cadastre.lat,format_toponyme(self.cadastre.name).replace('\'','\'\''),self.osm.name.replace('\'','\'\''),self.fantoir.name.replace('\'','\'\''),self.fantoir.fantoir,code_insee,code_dept,'CADASTRE',self.fantoir.bati)
            if self.has_fantoir:
                return "(ST_PointFromText('POINT({:7f} {:7f})',4326),'{:s}',null,'{:s}','{:s}','{:s}','{:s}','','{:s}',{:s},'')".format(self.cadastre.lon,self.cadastre.lat,format_toponyme(self.cadastre.name).replace('\'','\'\''),self.fantoir.name.replace('\'','\'\''),self.fantoir.fantoir,code_insee,code_dept,'CADASTRE',self.fantoir.bati)
            if self.has_osm:
                return "(ST_PointFromText('POINT({:7f} {:7f})',4326),'{:s}','{:s}',null,null,'{:s}','{:s}','','{:s}',null,'')".format(self.cadastre.lon,self.cadastre.lat,format_toponyme(self.cadastre.name).replace('\'','\'\''),self.osm.name.replace('\'','\'\''),code_insee,code_dept,'CADASTRE')
            return "(ST_PointFromText('POINT({:7f} {:7f})',4326),'{:s}',null,null,null,'{:s}','{:s}','','{:s}',null,'')".format(self.cadastre.lon,self.cadastre.lat,format_toponyme(self.cadastre.name).replace('\'','\'\''),code_insee,code_dept,'CADASTRE')
    def as_SQL_osm_row(self):
        if self.has_osm and self.has_fantoir:
            return "(ST_PointFromText('POINT({:7f} {:7f})',4326),null,'{:s}','{:s}','{:s}','{:s}','{:s}','','{:s}',{:s},'{:s}')".format(self.osm.lon,self.osm.lat,self.osm.name.replace('\'','\'\''),self.fantoir.name.replace('\'','\'\''),self.fantoir.fantoir,code_insee,code_dept,'OSM',self.fantoir.bati,self.osm.place)
        if self.has_osm:
            return "(ST_PointFromText('POINT({:7f} {:7f})',4326),null,'{:s}',null,null,'{:s}','{:s}','','{:s}',null,'{:s}')".format(self.osm.lon,self.osm.lat,self.osm.name.replace('\'','\'\''),code_insee,code_dept,'OSM',self.osm.place)
class Places:
    def __init__(self):
        self.p = {}

    def add_place(self,new_p):
        self.p[new_p.id]=new_p
    def match_fantoir(self,fantoir):
        for c in self.p:
            if c.fantoir and c.fantoir.fantoir and c.fantoir.fantoir == fantoir:
                return c
        return 0
    def match_name(self,name,target):
        # print("name : {:s}\n".format(name))
        res = []
        name_norm = normalize(name)
        if target == 'FANTOIR':
            for c in self.p:
                if self.p[c].fantoir and self.p[c].fantoir.name and self.p[c].fantoir.name_norm == name_norm:
                    res+=[c]
        if target == 'CADASTRE':
            for c in self.p:
                if c.cadastre and c.cadastre.name and c.cadastre.name_norm == name_norm:
                    res+=c
        if target == 'OSM':
            for c in self.p:
                if c.osm and c.osm.name and c.osm.name_norm == name_norm:
                    res+=c
        return res
    def _print(self):
        for c in self.p:
            print(self.p[c].osm.name)
            print(self.p[c].as_string())
    def _print_SQL_Cadastre(self):
        for c in self.p:
            print(self.p[c].as_SQL_cadastre_row())
    def as_SQL_Cadastre_array(self):
        a = []
        for c in self.p:
            if self.p[c].has_cadastre:
                a.append(self.p[c].as_SQL_cadastre_row())
        return a
    def as_SQL_OSM_array(self):
        a = []
        for c in self.p:
            if self.p[c].has_osm:
                a.append(self.p[c].as_SQL_osm_row())
        return a

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
    
    # Appostrophes initiale
    dic_ajoute_apostrophe = {}
    dic_ajoute_apostrophe['d'] = 'd\''
    dic_ajoute_apostrophe['D'] = 'D\''
    dic_ajoute_apostrophe['l'] = 'l\''
    dic_ajoute_apostrophe['L'] = 'L\''

    if a_s[0] in dic_ajoute_apostrophe:
        a_s[0] = dic_ajoute_apostrophe[a_s[0]]
    
    s = ' '.join(a_s).replace('\' ','\'')
    if len(s.strip())>1 and s.strip()[-1] == '\'':
        s = s.strip()[0:-1]
    return s
def get_data_from_pg(data_type,insee_com,local=False,suffixe_data=None):
    cache_file = get_cache_filename(data_type,insee_com)
    if not use_cache or not os.path.exists(cache_file) or (time.time() - os.path.getmtime(cache_file)) > 86400 :
        fq = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(data_type)),'r')
        str_query = fq.read().replace('__com__',insee_com)
        # print(str_query)
        fq.close()
        if local:
            pgc = get_pgc()
        else:
            pgc = get_pgc_layers()
        if suffixe_data:
            str_query = str_query.replace('__suffixe_data__',suffixe_data)
        cur = pgc.cursor()
        cur.execute(str_query)
        f = open(cache_file,'w+')
        for lt in cur:
            l = list(lt)
            f.write(str(l)+'\n')
        cur.close()
        f.seek(0)
    else :
        f = open(cache_file,'r')
        # print('open cache '+cache_file)
    res = []
    for l in f:
        res.append(eval(l))
    f.close()
    return res
def load_cadastre():
    # fname = get_cache_filename('cadastre_2_places',code_insee)
    # if os.path.exists(fname):
        # date_buildings_en_base = get_cadastre_etape_timestamp_debut(code_insee,'importBuildings','CADASTRE')
        # date_cache = os.path.getmtime(fname)
        # print('date_buildings_en_base '+str(date_buildings_en_base))
        # print('date_cache '+str(date_cache))
        # if date_cache > date_buildings_en_base:
            # os.utime(fname, None)
            # print('utime')
    data = get_data_from_pg('cadastre_2_places',code_insee,True)
    for d in data:
        print(d)
        targets = places.match_name(d[2],'FANTOIR')
        if targets:
            for t in targets:
                places.p[t].update_cadastre(d[0],d[1],d[2])
        else:
            places.add_place(Place(d[0],d[1],'','',d[2],'','',d[3],-1))
def load_dicts():
    dicts['lettre_a_lettre']= {'A':[u'Â',u'À'],
                        'C':[u'Ç'],
                        'E':[u'È',u'Ê',u'É',u'Ë'],
                        'I':[u'Ï',u'Î'],
                        'O':[u'Ö',u'Ô'],
                        'U':[u'Û',u'Ü'],
                        'OE':[u'Œ']}
    dicts['mot_a_blanc'] = ['DE LA','DU','DES','LE','LA','LES','DE','D','L']

def load_fantoir(insee):
    pgc = get_pgc()
    str_query = "SELECT code_insee||id_voie||cle_rivoli,\
                        TRIM(BOTH FROM nature_voie||' '||libelle_voie),\
                        ld_bati\
                FROM    fantoir_voie\
                WHERE    code_insee = '{:s}' AND\
                        type_voie = '3' AND\
                        COALESCE(caractere_annul,'') = '';".format(insee)
    cur_fantoir = pgc.cursor()
    cur_fantoir.execute(str_query)
    for c in cur_fantoir:
        p = Place(0,0,'',c[1],'','','',c[0],c[2])
        places.add_place(p)
def    load_osm():
    data = get_data_from_pg('place_insee',code_insee)
    for d in data:
        name = d[3]
        targets = places.match_name(name,'FANTOIR')
        if targets:
            # if len(targets)>1: print '**************\n'+str(targets)
            for t in targets:
                places.p[t].update_osm(d[0],d[1],d[2],name,d[4])
        else:
            places.add_place(Place(d[0],d[1],d[2],'','',name,'',d[4],-1))
    # places._print()
    # os._exit(0)
def load_to_db(places):
    table = 'cumul_places'
    sload = "DELETE FROM {:s} WHERE insee_com = '{:s}'".format(table,code_insee)
    pgc = get_pgc()
    cur_insert = pgc.cursor()
    cur_insert.execute(sload)

    a_values_place = []

    sload = 'INSERT INTO {:s} (geometrie,libelle_cadastre,libelle_osm,libelle_fantoir,fantoir,insee_com,dept,code_postal,source,ld_bati,ld_osm) VALUES'.format(table)
    # a_values = [places.p[a].as_SQL_cadastre_row() for a in places.p]
    a_values = places.as_SQL_Cadastre_array()
    nb_rec = len(a_values)
    if nb_rec>0:
        cur_insert.execute(sload+','.join(a_values)+';COMMIT;')
    # a_values = [places.p[a].as_SQL_osm_row() for a in places.p]
    a_values = places.as_SQL_OSM_array()
    if len(a_values)>0:
        cur_insert.execute(sload+','.join(a_values)+';COMMIT;')
    nb_rec+=len(a_values)
    return(nb_rec)
def normalize(s):
    s = s.upper()                # tout en majuscules
    s = s.split(' (')[0]        # parenthèses : on coupe avant
    s = s.replace('-',' ')        # separateur espace
    s = s.replace('\'',' ')        # separateur espace
    s = s.replace('’',' ')        # separateur espace
    s = s.replace('/',' ')        # separateur espace
    s = s.replace(':',' ')        # separateur deux points
    s = ' '.join(s.split())        # separateur : 1 espace

    for l in iter(dicts['lettre_a_lettre']):
        for ll in dicts['lettre_a_lettre'][l]:
            s = s.replace(ll,l)
    # s = s.encode('ascii','ignore')

    for c in dicts['mot_a_blanc']:
        s = s.replace(' '+c+' ',' ') #en cours de mot
        if s[0:len(c)+1] == c+' ':
            s = s[len(c)+1:]

    return s

def main(args):
    debut_total = time.time()
    usage = 'USAGE : python place_2_db.py <code INSEE> {use_cache=True}'
    if len(args) < 2:
        print(usage)
        os._exit(0)

    global pgc,fantoir,source,code_insee,code_dept,dicts,use_cache,places
    
    code_insee = args[1]
    dicts = {}
    load_dicts()
    # code_cadastre = get_code_cadastre_from_insee(code_insee)
    code_dept = get_cadastre_code_dept_from_insee(code_insee)
    format_cadastre = get_cadastre_format(code_insee)

    use_cache = True
    if len(args) > 2:
        use_cache = args[2]
    places = Places()
    load_fantoir(code_insee)
    
    batch_id_osm = batch_start_log('OSM','cumulPlaces',code_insee)

    if format_cadastre == 'VECT':
        batch_id_cadastre = batch_start_log('CADASTRE','cumulPlaces',code_insee)
        load_cadastre()
    load_osm()
        
    nb_rec = load_to_db(places)
    batch_end_log(nb_rec,batch_id_osm)
    if format_cadastre == 'VECT':
        batch_end_log(nb_rec,batch_id_cadastre)

if __name__ == '__main__':
    main(sys.argv)

