#!/usr/bin/env python
# coding: UTF-8

# import re
from collections import defaultdict


from . import db
# from . import helpers as hp
from .sources import fantoir
from .sql import sql_get_data
# from . import core as c


class Adresse:
    def __init__(self, x, y, num, source, voie=None, place=None, fantoir=None, code_postal=None, sous_commune_code=None, sous_commune_nom=None):
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

    def _as_string(self):
        return (f"source : {self.source}, numero : {self.numero}, voie : {self.voie}, place : {self.place}, fantoir : {self.fantoir}, code_postal:{self.code_postal}, sous_commune : {self.sous_commune_code} - {self.sous_commune_nom}")


class Adresses:
    def __init__(self, code_insee):
        self.a = {}
        self.liste = []
        self.index_by_voie = defaultdict(list)
        self.code_insee = code_insee
        self.noms_de_voies = set()

    # def __contains__(self, item):
    #     return item in self.a

    def __getitem__(self, key):
        return self.liste[key]

    # def __setitem__(self, key, value):
    #     self.a[key] = value

    def __iter__(self):
        return iter(self.liste)

    def add_adresse(self,ad):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        # if (ad.fantoir == None or hp.is_valid_fantoir(ad.fantoir, self.code_insee)) and hp.is_valid_housenumber(ad.numero):
        self.liste.append(ad)
        self.index_by_voie[ad.voie].append(len(self.liste)-1)
        self.noms_de_voies.add(ad.voie)

    def charge_numeros_ban(self):
        data = sql_get_data('numeros_ban',dict(code_insee=self.code_insee),db.bano_sources)
        for numero, voie, lon, lat, code_postal, code_insee_ac, nom_ac in data:
            self.add_adresse(Adresse(lon,lat,numero,'BAN',voie=voie,code_postal=code_postal,sous_commune_code=code_insee_ac,sous_commune_nom=nom_ac))
