#!/usr/bin/env python
# coding: UTF-8

from .models import Noms, Adresses, Topo

def process(source,code_insee,dept,**kwargs):
    topo = Topo(code_insee)
    adresses = Adresses(code_insee,source)
    noms = Noms(code_insee,source)

    if source == 'OSM':
        adresses.charge_noms_osm()
        adresses.charge_numeros_osm()

    if source == 'BAN':
        adresses.charge_numeros_ban()

    adresses.noms_des_adresses(noms)
    noms.add_fantoir(topo)
    adresses.enregistre()
    noms.enregistre()
