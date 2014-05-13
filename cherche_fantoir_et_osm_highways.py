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



""" 
    Cherche le code FANTOIR et les highways d'OSM
    correspondants à chaque relation associatedStreet.

    Ce code apelle des script du projet associatedStreet:
    https://github.com/vdct/associatedStreet/

    Ce Code est basé sur associatedStreet/addrfantoir.py
"""

import sys
import os.path
import subprocess
import urllib2
import shutil
import urllib
import collections
from zipfile import ZipFile

import cadastre 
from osm import OsmParser, OsmWriter
from mytools import write_stream_to_file
from mytools import to_ascii

ASSOCIATEDSTREET_GIT = "https://github.com/vdct/associatedStreet.git"
ASSOCIATEDSTREET_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "associatedStreet")

FANTOIR_URL = "http://www2.impots.gouv.fr/documentation/fantoir/"
FANTOIR_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fantoir")
FANTOIR_TXT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fantoir.txt")


# Clone le projet associatedStreet:
if not os.path.exists(ASSOCIATEDSTREET_DIR):
   subprocess.check_call(["git", "clone", ASSOCIATEDSTREET_GIT, ASSOCIATEDSTREET_DIR])
associatedStreet_init = os.path.join(ASSOCIATEDSTREET_DIR,"__init__.py")
if not os.path.exists(associatedStreet_init):
    open(associatedStreet_init, "a").close()
associatedStreet_pg_connextion = os.path.join(ASSOCIATEDSTREET_DIR,"pg_connexion.py")
if not os.path.exists(associatedStreet_pg_connextion):
    shutil.copyfile(associatedStreet_pg_connextion + ".txt", associatedStreet_pg_connextion)


import associatedStreet.addr_fantoir_building as addr_fantoir_building

addr_fantoir_building.dicts = addr_fantoir_building.Dicts()
addr_fantoir_building.dicts.load_lettre_a_lettre()
addr_fantoir_building.dicts.load_abrev_type_voie()
addr_fantoir_building.dicts.load_abrev_titres()
addr_fantoir_building.dicts.load_chiffres()
addr_fantoir_building.dicts.load_chiffres_romains()
addr_fantoir_building.dicts.load_mot_a_blanc()
addr_fantoir_building.dicts.load_osm_insee()

def normalize(nom):
    result = addr_fantoir_building.normalize(to_ascii(nom))
    if result.startswith("GR GRANDE RUE") or result.startswith("GR GRAND RUE"):
        result = result[3:]
    return result

def get_fantoir_txt_filename(code_departement):
    assert(len(code_departement) == 3)
    if code_departement[0] == '0':
        return code_departement[1:3] + '0.txt'
    else:
        return code_departement[0:3] + '.txt'

def get_fantoir_zip_filename(code_departement):
    wanted_filename = get_fantoir_txt_filename(code_departement)
    with open(FANTOIR_TXT,"r") as f:
        for line in f:
            zip_filename, txt_filename = line.strip().split("/")
            if txt_filename == wanted_filename:
                return zip_filename

def get_dict_fantoir(code_departement, code_commune):
    """ Retourne un dictionnaire qui mappe un nom normalizé 
        du Fantoir (nature + libele de la voie)
        vers le code Fantoir.
    """
    code_insee = cadastre.code_insee(code_departement, code_commune)
    try:
        addr_fantoir_building.pgc = addr_fantoir_building.get_pgc()
        addr_fantoir_building.dicts.load_fantoir(code_insee)
        assert(len(addr_fantoir_building.dicts.fantoir) > 0)
        return addr_fantoir_building.dicts.fantoir
    except:
        # La connexion avec la base SQL a du échouer, on 
        # charge les fichiers zip fantoir manuellement:
        dict_fantoir = {}
        zip_filename = get_fantoir_zip_filename(code_departement)
        filename = os.path.join(FANTOIR_DIR, zip_filename)
        ok_filename = filename + ".ok"
        if not (os.path.exists(filename) and os.path.exists(ok_filename)):
            sys.stdout.write("Téléchargement du fichier Fantoir " + zip_filename  + "\n")
            if os.path.exists(filename): os.remove(filename)
            if os.path.exists(ok_filename): os.remove(ok_filename)
            if not os.path.exists(FANTOIR_DIR): os.mkdir(FANTOIR_DIR)
            write_stream_to_file(urllib2.urlopen(FANTOIR_URL + zip_filename), filename)
            open(ok_filename, "a").close()
        else:
            sys.stdout.write("Lecture du fichier Fantoir " + zip_filename  + "\n")
        sys.stdout.flush()
        txt_filename = get_fantoir_txt_filename(code_departement)
        num_commune = code_insee[2:5]
        for line in ZipFile(filename, "r").open(txt_filename):
            if line[3:6] == num_commune:
               if line[108:109] != ' ':
                  # C'est un unregistrement de voie
                  if line[73] == ' ':
                      # la voie n'est pas annulée
                      assert(code_insee == line[0:2] + line[3:6])
                      id_voie = line[6:10]
                      cle_rivoli = line[10]
                      nature_voie = line[11:15].strip()
                      libele_voie = line[15:41].strip()
                      code_fantoir = code_insee + id_voie + cle_rivoli
                      nom_fantoir = nature_voie + " " + libele_voie
                      dict_fantoir[normalize(nom_fantoir)] = code_fantoir
        return dict_fantoir


def open_osm_overpass(requete, cache_filename, metropole=False):
    ok_filename = cache_filename + ".ok"
    if not (os.path.exists(cache_filename) and os.path.exists(ok_filename)):
        if os.path.exists(cache_filename): os.remove(cache_filename)
        if os.path.exists(ok_filename): os.remove(ok_filename)
        if metropole:
            # oapi-fr.openstreetmap.fr n'a que la métropole, pas l'outre mer
            overvass_server = "http://oapi-fr.openstreetmap.fr/oapi/interpreter?"
        else:
            overvass_server = "http://overpass-api.de/api/interpreter?"
        url = overvass_server + urllib.urlencode({'data':requete})
        sys.stdout.write((urllib.unquote(url) + "\n").encode("utf-8"))
        sys.stdout.flush()
        write_stream_to_file(urllib2.urlopen(url), cache_filename)
        open(ok_filename, "a").close()
    return OsmParser().parse(cache_filename)
            
def open_osm_multipolygon_s_ways_commune(code_departement, code_commune, type_multipolygon, filtre="", nodes=False):
    cache_filename = code_commune + "-multipolygon_" + type_multipolygon + "s.osm"
    code_insee = cadastre.code_insee(code_departement, code_commune)
    area = 3600000000 + addr_fantoir_building.dicts.osm_insee[code_insee]
    requete_overpass = 'rel(area:%d)[type=multipolygon]["%s"]%s;way(r);' % (area, type_multipolygon, filtre)
    if nodes: requete_overpass += "(._;>;);"
    requete_overpass += "out meta;"
    sys.stdout.write((u"Récupération des multipolygon " + type_multipolygon + " de la commune\n").encode("utf-8"))
    return open_osm_overpass(requete_overpass, cache_filename, metropole=code_departement.startswith("0"))

def open_osm_ways_commune(code_departement, code_commune, type_way, filtre="", nodes=False):
    cache_filename = code_commune + "-" + type_way + "s.osm"
    code_insee = cadastre.code_insee(code_departement, code_commune)
    area = 3600000000 + addr_fantoir_building.dicts.osm_insee[code_insee]
    requete_overpass = 'way(area:%d)["%s"]%s;' % (area, type_way, filtre)
    if nodes: requete_overpass += "(._;>;);"
    requete_overpass += "out meta;"
    sys.stdout.write((u"Récupération des " + type_way + " de la commune\n").encode("utf-8"))
    return open_osm_overpass(requete_overpass, cache_filename, metropole=code_departement.startswith("0"))

    
def get_dict_osm_ways(osm):
    """ Pour le fichier osm donné, retourne un dictionnaire qui mappe le
        nom normalisé des ways vers un dictionnaire avec:
         - un chanps 'name' avec le nom original
         - un champ 'ids' avec la liste des id des ways ayant ce 
           nom normalizé là.
    """
    dict_ways_osm = {}
    for way in osm.ways.itervalues():
        name = way.tags['name']
        name_norm = normalize(name)
        if name and name_norm:
            if name_norm not in dict_ways_osm:
                dict_ways_osm[name_norm] = {'name':name,'ids':[]}
            dict_ways_osm[name_norm]['ids'].append(way.id())
    return dict_ways_osm

def humanise_nom_fantoir(name, dict_premier_mot, dict_tout_les_mots):
    original_name = name
    name = name.title()
    mots = name.split()
    premier_mot_norm = to_ascii(mots[0]).upper()
    if premier_mot_norm in dict_premier_mot:
        if len(mots) > 1 and mots[1] == dict_premier_mot[premier_mot_norm]:
            # Le type de voie est répété dans le nom de la voie, ça arrive parfois, on le supprime:
            mots = mots[1:]
        else:
            # On remplace étend le préfixe:
            mots = dict_premier_mot[premier_mot_norm].split() + mots[1:]
    for i,mot in enumerate(mots):
        mot_norm = to_ascii(mot).upper()
        if mot_norm in dict_tout_les_mots:
            mots[i] = dict_tout_les_mots[mot_norm]
    name = ' '.join(mots)
    name = name.replace(" Du "," du ")
    name = name.replace(" De La "," de la ")
    name = name.replace(" De "," de ")
    name = name.replace(" Des "," des ")
    name = name.replace(" Et "," et ")
    name = name.replace(" L "," l'")
    name = name.replace(" L'"," l'")
    name = name.replace(" D "," d'")
    name = name.replace(" D'"," d'")
    name = name.replace(" Saint "," Saint-")
    name = name.replace(" Sainte "," Sainte-")
    name = name.replace("Grande Rue Grande Rue", "Grande Rue")
    name = name.replace("Grande Rue Grand Rue", "Grand'Rue")
    #if name != original_name:
    #    print " - ", original_name, "=>", name
    return name


def get_dict_abrev_type_voie():
    """ Retourne un dictionnaire qui transforme une abréviation de type de voie
        utilisée par le Fantoir en sa version non abrégée.
    """
    dict_abrev_type_voie = {}
    for nom, abrev in addr_fantoir_building.dicts.abrev_type_voie.iteritems():
        nom = nom.title()
        abrev = to_ascii(abrev).upper()
        if not abrev in dict_abrev_type_voie:
            dict_abrev_type_voie[abrev] = nom
        else:
            # Choisi le nom le plus petit:
            if len(nom) < len(dict_abrev_type_voie[abrev]):
                dict_abrev_type_voie[abrev] = nom
    dict_abrev_type_voie["CHEM"] = "Chemin" # à la place de CHEMINEMENT
    dict_abrev_type_voie["CHE"] = "Chemin" # à la place de CHEM
    dict_abrev_type_voie["ILE"] = u"Île" # pb d'encodage dans le projet associatedStreet
    dict_abrev_type_voie["ECA"] = u"Écart" # pb d'encodage dans le projet associatedStreet
    return dict_abrev_type_voie

def get_dict_accents_mots(osm_noms):
    """Retourne un dictionnaire qui transforme un mot (ascii majuscule)
       en sa version avec accents.
       Pour cela on utilise en entrée le fichier osm CODE_COMUNE-noms.osm,
       qui contient les mots extraits des export PDF du cadastre.
    """
    dict_accents_mots = {}
    if osm_noms:
        sys.stdout.write((u"Recherche l'orthographe accentuée depuis les exports PDF du cadastre.\n").encode("utf-8"))
        liste_mots_a_effacer_du_dict = ["DE", "LA", "ET"]
        # On essaye de parser l'ensemble des noms extraits du cadastre pour
        # en faire un dictionaire de remplacement a appliquer
        for node in osm_noms.nodes.itervalues():
          if not 'place' in node.tags: # on évite les nœuds place=neighbourhood qui sont écrit en majuscule sans accents
            for mot in node.tags['name'].replace("_"," ").replace("-"," ").split():
                if len(mot) > 1:
                    mot_norm = to_ascii(mot).upper()
                    if mot_norm != mot.upper(): # il contient des accents
                        mot = mot.capitalize()
                        if mot_norm not in dict_accents_mots:
                            dict_accents_mots[mot_norm] = mot
                        elif dict_accents_mots[mot_norm] != mot:
                            alternative = dict_accents_mots[mot_norm]
                            # On a deux orthographes pour le même mot, on garde celle avec des caracères
                            # bizares, genre accents ou cédille
                            mot_est_complexe = to_ascii(mot) != mot
                            alternative_est_complexe = to_ascii(alternative) != alternative
                            if mot_est_complexe and not alternative_est_complexe:
                                dict_accents_mots[mot_norm] = mot
                            elif alternative_est_complexe and not mot_est_complexe:
                                # on garde l'arternative qui est actuellement dans le dictionnaire
                                pass
                            elif alternative_est_complexe and mot_est_complexe:
                                # je ne sais pas quoi faire, trop de risque pour cette orthographe
                                # on supprime le mot
                                liste_mots_a_effacer_du_dict.append(mot_norm)
                                sys.stdout.write(("ATTENTION: ne peut pas choisir entre l'orthographe " + mot + " ou " + alternative + "\n").encode("utf-8"))
                            else:
                                # c'est juste un problème de capitale, on ignore
                                pass
        for mot in liste_mots_a_effacer_du_dict:
            if mot in dict_accents_mots:
                del(dict_accents_mots[mot])
    dict_accents_mots.update({
        "EGLISE": u"Église", 
        "ECOLE": u"École", 
        "ECOLES": u"Écoles", 
        "ALLEE": u"Allée", 
        "ALLEES": u"Allées",
        "GENERAL" : u"Général",
        # Abréviations typiques du Fantoir:
        "PDT": u"Président",
        "CDT": "Commandant",
        "REGT" : u"Régiment",
        "DOC" : "Docteur",
        "ST" : "Saint",
        "STE" : "Sainte",
    })
    return dict_accents_mots


def cherche_fantoir_et_osm_highways(code_departement, code_commune, osm, osm_noms = None):
    """ Modifie les relations associatedStreet du fichier osm donné,
        à partir de la version normalizée de leur nom:
         - positionne le tag ref:FR:FANTOIR avec le code fantoir correspondant
         - cherche depuis les données OSM les highways de la commune ayant le
           même nom normalizé, et les ajoute en tant que role street de la 
           relation
         - change le nom de la relation en celui des highway OSM si trouvé, 
           ou sinon humanise le nom original en utilisant les accents trouvé 
           dans le fichier osm_noms passé en paramètre.
    """
    sys.stdout.write((u"Rapprochement avec les codes FANTOIR, et les highway OSM\n").encode("utf-8"))
    highways_osm = open_osm_ways_commune(code_departement, code_commune, "highway", '["name"]', nodes=False)
    dict_ways_osm = get_dict_osm_ways(highways_osm)
    dict_fantoir = get_dict_fantoir(code_departement, code_commune)
    dict_abrev_type_voie = get_dict_abrev_type_voie()
    dict_accents_mots = get_dict_accents_mots(osm_noms)

    log = open(code_commune + "-associatedStreet.log", "w")

    nb_associatedStreet = 0
    nb_voies_fantoir = 0
    nb_voies_osm = 0

    # Compte le nombre d'occurence de chaque nom normalizé
    # afin de détecter les conflits
    conflits_normalization = collections.Counter([
        normalize(r.tags['name']) for r in osm.relations.itervalues() 
        if r.tags.get('type') == 'associatedStreet'])
  

    for relation in osm.relations.itervalues():
        if relation.tags['type'] == 'associatedStreet':
            nb_associatedStreet += 1
            name = relation.tags['name']
            name_norm = normalize(name)
            if name and name_norm:
                log.write((name + u" => normalizé[" + name_norm + "]").encode("utf-8"))
                if conflits_normalization[name_norm] > 1:
                    # Cas rencontré à Dijon (021 B0231), deux rues différentes "Rue la Fontaine" et "Rue de Fontaine" 
                    # ont le même nom normalizé, on ne tente donc pas de raprochement Fantoir ou OSM
                    relation.tags['name'] = humanise_nom_fantoir(name, dict_abrev_type_voie, dict_accents_mots)
                    log.write((" CONFLIT DE NORMALIZATION, => " + relation.tags['name'] + "\n").encode("utf-8"))
                else:
                    if name_norm in dict_fantoir:
                        relation.tags['ref:FR:FANTOIR'] = dict_fantoir[name_norm]
                        nb_voies_fantoir += 1
                        log.write((" ref:FR:FANTOIR[" + dict_fantoir[name_norm] + "]").encode("utf-8"))
                    else:
                        log.write((" ref:FR:FANTOIR[???]").encode("utf-8"))
                    if name_norm in dict_ways_osm:
                        nb_voies_osm += 1
                        for id_way in dict_ways_osm[name_norm]['ids']:
                            relation.add_member_type_ref_role('way', id_way, 'street')
                        relation.tags['name'] = dict_ways_osm[name_norm]['name']
                        log.write((" osm highway[" + relation.tags['name'] + "]\n").encode("utf-8"))
                    else:
                        relation.tags['name'] = humanise_nom_fantoir(name, dict_abrev_type_voie, dict_accents_mots)
                        log.write((" osm highway[???] => " + relation.tags['name'] + "\n").encode("utf-8"))
    log.close()
    sys.stdout.write(("Nombre de rues: "+str(nb_associatedStreet)+ "\n").encode("utf-8"))
    if nb_associatedStreet > 0:
      sys.stdout.write(("     avec code FANTOIR      : "+str(nb_voies_fantoir)+" ("+str(int(nb_voies_fantoir*100/nb_associatedStreet))+"%)\n").encode("utf-8"))
      sys.stdout.write(("     avec rapprochement OSM : "+str(nb_voies_osm)+" ("+str(int(nb_voies_osm*100/nb_associatedStreet))+"%)\n").encode("utf-8"))

    # Humanise aussi les noms de quartier:
    for node in osm.nodes.itervalues():
        if node.tags.has_key("place"):
            node.tags["name"] = humanise_nom_fantoir(
                node.tags["name"], dict_abrev_type_voie, dict_accents_mots)
    
def print_help():
    programme = sys.argv[0]
    spaces = " " * len(programme)
    sys.stdout.write((u"Récupération des code fantoir et des highway OSM des associatedStreet\n").encode("utf-8"))
    sys.stdout.write((u"USAGE:" + "\n").encode("utf-8"))
    sys.stdout.write((u"%s  CODE_DEPARTEMENT CODE_COMUNE input.osm output.osm" % programme + "\n").encode("utf-8"))

def command_line_error(message, help=False):
    sys.stdout.write(("ERREUR: " + message + "\n").encode("utf-8"))
    if help: print_help()


def main(argv):
    if len(argv) != 5 or argv[1] in ["-h","-help","--help"]:
        print_help()
        sys.exit()
    code_departement = argv[1]
    code_commune = argv[2]
    input_filename = argv[3]
    output_filename = argv[4]
    if len(code_departement) != 3:
        command_line_error("le code departement doit avoir 3 chiffres")
    if len(code_commune) != 5:
        command_line_error("le code commune doit avoir 5 lettres ou chiffres")
    osm = OsmParser().parse(input_filename)
    osm_noms = None
    osm_noms_filename = code_commune + "-noms.osm"
    if os.path.exists(osm_noms_filename):
        print "Charges les noms depuis le fichier " + osm_noms_filename
        osm_noms = OsmParser().parse(osm_noms_filename)
    cherche_fantoir_et_osm_highways(code_departement, code_commune, osm, osm_noms)
    OsmWriter(osm).write_to_file(output_filename)

if __name__ == '__main__':
    main(sys.argv)

