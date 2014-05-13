#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# It is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with it. If not, see <http://www.gnu.org/licenses/>.


import re
import rtree.index

bis_ter_quater = {
  'B' : "bis",
  'T' : "ter",
  'Q' : "quater",
  " bis" : "bis",
  " ter" : "ter",
  " quater" : "quater",
  " quinquies" : "quinquies",
}

RE_NUMERO_CADASTRE = re.compile("^([0-9][0-9]*)(( bis)|( ter)|( quater)|( quinquies)|([A-Za-z?]*))\\b", re.I)

DISTANCE_RECHERCHE_VOSINS_ORPHELINS = 100

def determine_osm_parcelles_bis_ter_quater(osm):
    series = {}
    for item in osm.ways.itervalues():
        for tag, value in item.tags.iteritems():
            if tag.startswith("addr") and tag.endswith(":street"):
                street = value
                housenumber = item.tags.get(tag.split(":")[0] + ":housenumber") or ""
                num_match = RE_NUMERO_CADASTRE.match(housenumber)
                if num_match:
                    numero = num_match.group(1)
                    lettre = num_match.group(2)
                    if lettre:
                        if not street in series: series[street] = {}
                        if not numero in series[street]: series[street][numero] = set()
                        series[street][numero].add(lettre)
    # On calcule pour chacune des serie si elle est en bis,ter,quater:
    is_bis_ter_quater = {
        rue: { 
            num: all([l in bis_ter_quater for l in lettres]) 
            for num,lettres in lettres_numeros.iteritems()
        }
        for rue, lettres_numeros in series.iteritems()
    }
    for item in osm.ways.itervalues():
        for tag, value in item.tags.items():
            if tag.startswith("addr") and tag.endswith(":street"):
                street = value
                housenumber = item.tags.get(tag.split(":")[0] + ":housenumber") or ""
                num_match = RE_NUMERO_CADASTRE.match(housenumber)
                if num_match:
                    numero = num_match.group(1)
                    lettre = num_match.group(2)
                    if lettre:
                        if is_bis_ter_quater[street][numero]:
                            lettre = bis_ter_quater[lettre]
                        item.tags[tag.split(":")[0] + ":housenumber"] = numero + " " + lettre

def distance_x2((x1,y1), (x2,y2)):
    return (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)
    

def determine_osm_adresses_bis_ter_quater(osm):
    """Remplace, pour les nœuds addr:housenumber,
       les lettres qui suivent le numéro par bis, ter, quater
       si approprié.
       
       On fait la distinction entre les séries commencent à la lettre 
       A et qui peuvent faire tout l'alphabet, et celles commençant à 
       la lettres B qui se restreignent à B,T,Q,C.

       Pour les série de lettres A,B,C,... on les laisse tel quelle,
       mais en rajoutant juste un espace entre le numéro et la lettre.
       
       Pour les séries B,T,Q,C on les transforme en bis, ter, quater 
       et quinquies en minuscule avec aussi un espace pour le séparer
       du numéro.

       La difficulté consiste à différencier le cas A,B,C,D du cas
       bis,ter,quater pour les numéros orphelins (déssiné sur le cadastre)
       dont on a pas retrouvé la parcelle associée donc le nom de rue
       donc dont on ne peut pas s'assurer de la série à laquelle
       ils appartiennent.
    """

    series = {}
    housenumber_index = rtree.index.Index()
    for item in osm.iteritems():
        if item.tags.has_key("addr:housenumber"):
            num_match = RE_NUMERO_CADASTRE.match(item.tags["addr:housenumber"])
            if num_match:
                item.numero = num_match.group(1)
                item.lettre = num_match.group(2)
                item.street = item.tags.get("addr:street")
                housenumber_index.insert(item.id(), item.xy, (item.type(),item.id()))
                if item.lettre and item.street:
                    if not item.street in series: series[item.street] = {}
                    if not item.numero in series[item.street]: series[item.street][item.numero] = set()
                    series[item.street][item.numero].add(item.lettre)
    for relation in osm.relations.itervalues():
        #print relation, relation.tags.get("type"), relation.tags.get("name")
        if relation.tags.get("type") == "associatedStreet" and relation.tags.get("name"):
            street = relation.tags.get("name")
            if not street in series: series[street] = {}
            for member, role in osm.iter_relation_members(relation):
                if role == "house":
                    if member and hasattr(member, "lettre") and member.lettre:
                        member.street = street
                        if not member.numero in series[member.street]: series[member.street][member.numero] = set()
                        #print "serrie[" + member.street + "][" + member.numero + "].add(" + member.lettre + ")"
                        series[member.street][member.numero].add(member.lettre)

    DISTANCE_X2 = DISTANCE_RECHERCHE_VOSINS_ORPHELINS * DISTANCE_RECHERCHE_VOSINS_ORPHELINS
    for item in osm.iteritems():
        if hasattr(item, "lettre") and item.lettre and not item.street:
            # On a affaire a un numéro avec une lettre, mais orphelin (sans rue associée) 
            # on vas essyer de chercher dans le coin si il n'y aurais pas des numéros
            # identiques (mais avec potentiellement une lettre différente)
            x,y = item.xy
            search_bounds = (x-DISTANCE_RECHERCHE_VOSINS_ORPHELINS, y-DISTANCE_RECHERCHE_VOSINS_ORPHELINS,
                             x+DISTANCE_RECHERCHE_VOSINS_ORPHELINS, y+DISTANCE_RECHERCHE_VOSINS_ORPHELINS)
            item_series = set()
            for other_type,other_id in [e.object for e in housenumber_index.intersection(search_bounds, objects=True)]:
                other = osm.get(other_type, other_id)
                if other.numero == item.numero and other.lettre and distance_x2(item.xy, other.xy) < DISTANCE_X2:
                    if other.street:
                        series[other.street][item.numero].add(item.lettre)
                        item_series.update(series[other.street][item.numero])
                    else:
                        item_series.update(other.lettre)
            if all([lettre in bis_ter_quater for lettre in item_series]):
                item.lettre = bis_ter_quater[item.lettre]

    # Maintenant qu'on a traiter les numéros orhpelins du mieux qu'on a pu
    # ou vas traiter les numéros dont on connais la rue.
    # On calcule pour chacune des series si elle est en bis,ter,quater:
    is_bis_ter_quater = {
        rue: { 
            num: all([l in bis_ter_quater for l in lettres]) 
            for num,lettres in lettres_numeros.iteritems()
        }
        for rue, lettres_numeros in series.iteritems()
    }

    # On corrige les addr:housenumber pour correspondre au nos calculs, et on nettoi les champs qu'on avait ajouté:
    for item in osm.iteritems():
        if hasattr(item, "lettre"):
            if item.lettre:
                if item.street and is_bis_ter_quater[item.street][item.numero]:
                    item.lettre = bis_ter_quater[item.lettre]
                #print item.tags["addr:housenumber"] + " => " + item.numero + " " + item.lettre
                item.tags["addr:housenumber"] = item.numero + " " + item.lettre
            delattr(item, "numero")
            delattr(item, "lettre")
            delattr(item, "street")


