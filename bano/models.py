#!/usr/bin/env python
# coding: UTF-8

import io
import json
from collections import defaultdict,OrderedDict

from . import db
from . import helpers as hp
# from .sources import fantoir
from .sql import sql_get_data,sql_process

class Nom:
    def __init__(self,nom,fantoir,nature,source,code_insee,code_insee_ancienne_commune):
        self.code_insee = code_insee
        self.code_insee_ancienne_commune = code_insee_ancienne_commune
        self.nom = nom
        self.fantoir = fantoir
        self.nature = nature
        self.source = source
        self.nom_normalise = hp.normalize(nom)

    def __eq__(self,other):
        return (self.nom == other.nom and self.fantoir == other.fantoir and self.nature == other.nature and self.source == other.source and self.code_insee == other.code_insee)
        # return (self.nom == other.nom and self.fantoir == other.fantoir)

    def __hash__(self):
        return hash((self.nom,self.fantoir,self.source,self.nature,self.code_insee))
        # return hash((self.nom,self.fantoir))

    def _as_csv_format_bano(self):
        return f"{self.fantoir}${self.nom}${self.nature}${self.code_insee}${self.code_insee_ancienne_commune}${self.source}"

    def add_fantoir(self,topo):
        if not self.fantoir:
            self.fantoir = topo.topo.get(self.nom_normalise)

class Noms:
    def __init__(self, code_insee,source):
        self.code_insee = code_insee
        self.source = source
        self.triplets_nom_fantoir_source = []

    # On ne charge pas les noms des numeros OSM. Ils sont ajoutés via Adresses.nom_des_adresses
    def charge_noms_osm_hors_numeros(self):
        data = sql_get_data('charge_noms_voies_lieux-dits_OSM',dict(code_insee=self.code_insee),db.bano_sources)+sql_get_data('charge_noms_voies_relation_bbox_OSM',dict(code_insee=self.code_insee),db.bano_sources)+sql_get_data('charge_noms_voies_relation_OSM',dict(code_insee=self.code_insee),db.bano_sources)
        for provenance,name,tags,libelle_suffixe,ac_code_insee,ac_nom,nature in data:
            if provenance in (1,2,3,4,5):
                self.add_nom(Nom(name,tags.get('ref:FR:FANTOIR'),nature,'OSM',self.code_insee,ac_code_insee))
            if provenance in (6,7) and tags.get('ref:FR:FANTOIR'):
                self.add_nom(Nom(name,tags['ref:FR:FANTOIR'],nature,'OSM',self.code_insee,ac_code_insee))

    # On ajoute un nom s'il n'a pas de FANTOIR ou si son FANTOIR appartient à la commune
    def add_nom(self,nom=Nom):
        if not nom.fantoir or nom.fantoir[0:5] == self.code_insee:
            self.triplets_nom_fantoir_source.append(nom)

    def add_fantoir(self,topo):
        for t in self.triplets_nom_fantoir_source:
            t.add_fantoir(topo)

    def enregistre(self):
        sql_process('suppression_noms_commune_source',dict(code_insee=self.code_insee,source=self.source),db.bano)
        io_in_csv = io.StringIO()
        for t in set(self.triplets_nom_fantoir_source):
            if t.fantoir:
                io_in_csv.write(t._as_csv_format_bano()+'\n')
        io_in_csv.seek(0)
        with db.bano.cursor() as cur_insert:
            cur_insert.copy_from(io_in_csv, "nom_fantoir", sep='$',null='',columns=('fantoir','nom','nature','code_insee','code_insee_ancienne_commune','source'))

class Adresse:
    def __init__(self, code_insee, x, y, num, source, voie=None, place=None, fantoir=None, code_postal=None, sous_commune_code=None, sous_commune_nom=None):
        self.code_insee = code_insee
        self.x = x
        self.y = y
        self.source = source
        self.numero = num
        self.voie = voie
        self.place = place
        self.fantoir = fantoir
        self.code_postal = code_postal
        self.sous_commune_code = sous_commune_code
        self.sous_commune_nom = sous_commune_nom
        self.voie_normalisee = hp.normalize(self.voie) if self.voie else None
        self.place_normalisee = hp.format_toponyme(self.place) if self.place else None

    def __hash__(self):
        return hash((self.code_insee,self.source,self.numero,self.voie,self.place,self.sous_commune_code))

    def __eq__(self,other):
        return (self.code_insee == other.code_insee and self.source == other.source and self.numero == other.numero and self.voie == other.voie and self.place == other.place and self.sous_commune_code == other.sous_commune_code)

    def _as_csv_format_bano(self):
        return f"{self.fantoir if self.fantoir else ''}${self.x}${self.y}${self.numero}${self.voie if self.voie else ''}${self.place if self.place else ''}${self.code_postal}${self.code_insee}${self.sous_commune_code if self.sous_commune_code else ''}${self.source}"

    def _as_string(self):
        return (f"source : {self.source}, numero : {self.numero}, voie : {self.voie} ({self.voie_normalisee}), place : {self.place}, fantoir : {self.fantoir}, code_postal:{self.code_postal}, sous_commune : {self.sous_commune_code} - {self.sous_commune_nom}")

class Adresses:
    def __init__(self, code_insee,source):
        self.code_insee = code_insee
        self.source = source
        self.liste = set()
        self.index_voie = defaultdict(list)
        self.noms_de_voies = set()

    # def __contains__(self, item):
    #     return item in self.a

    def __getitem__(self, key):
        return self.liste[key]

    # def __setitem__(self, key, value):
    #     self.a[key] = value

    def __iter__(self):
        return iter(self.liste)

    def _print(self,pattern=None):
        for a in self:
            if not pattern or pattern in a._as_string():
                print(a._as_string())


    def add_adresse(self,ad):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        # if (ad.fantoir == None or hp.is_valid_fantoir(ad.fantoir, self.code_insee)) and hp.is_valid_housenumber(ad.numero):
        self.liste.add(ad)
        self.index_voie[ad.voie].append(len(self.liste)-1)
        self.noms_de_voies.add(ad.voie)

    # def add_fantoir(self):
    #     for nom in self.noms:
    #         fantoir = topo.topo.get(a.voie_normalisee) 
      
    def charge_numeros_ban(self,topo):
        data = sql_get_data('charge_ban_commune',dict(code_insee=self.code_insee),db.bano_sources)
        for id_fantoir, numero, voie, lon, lat, code_postal, code_insee_ac, nom_ac in data:
            if id_fantoir:
                fantoir9 = f"{id_fantoir[0:5]}{id_fantoir[6:10]}"
                fantoir = topo.code_fantoir9_vers_fantoir10.get(fantoir9)
            else:
                fantoir = None
            self.add_adresse(Adresse(self.code_insee,lon,lat,numero,'BAN',voie=voie,fantoir=fantoir,code_postal=code_postal,sous_commune_code=code_insee_ac,sous_commune_nom=nom_ac))

    def charge_numeros_osm(self):
        data = sql_get_data('charge_numeros_OSM',dict(code_insee=self.code_insee),db.bano_sources)+sql_get_data('charge_numeros_bbox_OSM',dict(code_insee=self.code_insee),db.bano_sources)

        for lon, lat, provenance, numero, voie, place, tags, suffixe, code_postal, code_insee_ac, nom_ac in data:

            fantoir = tags.get('ref:FR:FANTOIR')
            if fantoir and not hp.fantoir_valide(fantoir,self.code_insee):
                print("fantoir invalide",fantoir,self.code_insee)
                continue

            if provenance in (1,2,):
                self.add_adresse(Adresse(self.code_insee,lon,lat,numero,'OSM',voie=voie,place=place,fantoir=fantoir,code_postal=code_postal,sous_commune_code=code_insee_ac,sous_commune_nom=nom_ac))
            if provenance in (3,4,) and tags.get('name'):
                self.add_adresse(Adresse(self.code_insee,lon,lat,numero,'OSM',voie=tags['name'],place=None,fantoir=fantoir,code_postal=code_postal,sous_commune_code=code_insee_ac,sous_commune_nom=nom_ac))
            if provenance in (5,6,) and tags.get('name') and tags.get('ref:FR:FANTOIR'):
                if tags['ref:FR:FANTOIR'][0:5] == self.code_insee:
                    self.add_adresse(Adresse(self.code_insee,lon,lat,numero,'OSM',voie=tags['name'],place=None,fantoir=tags['ref:FR:FANTOIR'],code_postal=code_postal,sous_commune_code=code_insee_ac,sous_commune_nom=nom_ac))

    def noms_des_adresses(self,noms):
        for a in self:
            if a.voie:
                noms.add_nom(Nom(a.voie,a.fantoir,'voie',a.source,self.code_insee,a.sous_commune_code))
            if a.place:
                noms.add_nom(Nom(a.place,a.fantoir,'place',a.source,self.code_insee,a.sous_commune_code))

    def enregistre(self):
        sql_process('suppression_adresses_commune_source',dict(code_insee=self.code_insee,source=self.source),db.bano)
        io_in_csv = io.StringIO()
        for a in self:
            io_in_csv.write(a._as_csv_format_bano()+'\n') # separateur $ car on trouve des virgules dans le contenu
        io_in_csv.seek(0)
        with db.bano.cursor() as cur_insert:
            cur_insert.copy_from(io_in_csv, "bano_adresses", sep='$',null='',columns=('fantoir','lon','lat','numero','nom_voie','nom_place','code_postal','code_insee','code_insee_ancienne_commune','source'))


class Topo:
    def __init__(self, code_insee):
        self.code_insee = code_insee
        self.topo = OrderedDict()
        self.code_fantoir9_vers_fantoir10 = {}

        # self.index_by_nom_normalise = defaultdict(list)

        self.charge_topo()

    def __iter__(self):
        return iter(self.topo.items())

    # def __contains__(self, item):
    #     return item in self.a

    def __getitem__(self, key):
        return self.topo[key]

    def _print(self,pattern=None):
        for k,v in self:
            if not pattern or pattern in v:
                print(f"{k} : {v}")

    def charge_topo(self):
        data = sql_get_data('charge_topo_commune',dict(code_insee=self.code_insee),db.bano_sources)
        for fantoir,nom in data:
            nom = hp.normalize(' '.join(nom.replace('-',' ').split()))
            self.topo[fantoir] = nom
            self.code_fantoir9_vers_fantoir10[fantoir[0:9]] = fantoir
            self.topo[nom] = fantoir
