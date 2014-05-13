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

""" Tente d'extraire les mots (nom de rue ou de lieu)
    depuis le cadastre au format pdf.
"""


import sys
import math
import os.path

from osm import Osm,Node,Way,OsmWriter
from pdf_vers_osm_housenumbers import CadastreParser
from pdf_vers_osm_housenumbers import TextPathRecognizer
from pdf_vers_osm_housenumbers import CadastreToOSMTransform

THIS_DIR = os.path.dirname(__file__)
REFERENCE_NOM_DE_RUE = os.path.join(THIS_DIR, "reference-noms_de_rue.svg")
REFERENCE_NOM_DE_QUARTIER = os.path.join(THIS_DIR, "reference-noms_de_quartier.svg")


class NamePathRecognizer(object):
    def __init__(self):
        self.nom_rue_recognizer = TextPathRecognizer(tolerance=0.05, min_scale=0.9, max_scale=1.1)
        self.nom_rue_recognizer.load_from_svg(REFERENCE_NOM_DE_RUE)
        self.nom_quartier_recognizer = TextPathRecognizer(tolerance=0.05, min_scale=0.9, max_scale=1.1, force_horizontal=True)
        self.nom_quartier_recognizer .load_from_svg(REFERENCE_NOM_DE_QUARTIER)
        # Il y a parfois des noms écrits en petit, pour les des lotissement par exemple, on réutilise
        # la même base de donnée utilisée pour les nom de rues mais en diminuant la taille (scale):
        self.petit_nom_recognizer = TextPathRecognizer(tolerance=0.05, min_scale=0.55, max_scale=0.69, force_horizontal=True)
        self.petit_nom_recognizer.database = self.nom_rue_recognizer.database
        self.petit_nom_recognizer.space_width = self.nom_rue_recognizer.space_width * (self.petit_nom_recognizer.max_scale + self.petit_nom_recognizer.min_scale) / (self.nom_rue_recognizer.max_scale + self.nom_rue_recognizer.min_scale)
        self.rues = []
        self.quartiers = []
    def handle_path(self, path, transform):
        found = self.nom_quartier_recognizer.recognize(path)
        for recognizer, liste in [(self.nom_quartier_recognizer, self.quartiers), (self.petit_nom_recognizer, self.rues), (self.nom_rue_recognizer, self.rues)]:
            found = recognizer.recognize(path)
            if found:
                text, position, angle = found
                # On rejette les mots commencant par un chiffre:
                if not ord(text[0]) in range(ord('0'), ord('9')+1):
                    liste.append((text, transform(position), angle))
                    if text.find("???") == -1: 
                        return True
        return False        

def osm_add_node(osm, (lon,lat)):
    n = Node({'lon':str(lon),'lat':str(lat)})
    osm.add_node(n)
    return n

def pdf_vers_cadastre_noms(pdf_filename_list):
    noms_recognizer = NamePathRecognizer()
    cadastre_parser = CadastreParser([noms_recognizer.handle_path])
    for pdf_filename in pdf_filename_list:
        cadastre_parser.parse(pdf_filename)
    return cadastre_parser.cadastre_projection, noms_recognizer.quartiers, noms_recognizer.rues

def pdf_vers_osm_noms(pdf_filename_list, osm_output):
    projection, quartiers, rues = pdf_vers_cadastre_noms(pdf_filename_list)
    cadastre_to_osm_transform = CadastreToOSMTransform(projection).transform_point
    osm = Osm({'upload':'false'})
    for nom, position, angle in quartiers:
        node = osm_add_node(osm, cadastre_to_osm_transform(position))
        node.tags['name'] = nom
        if nom.lower().split()[0]== "hameau":
            node.tags['place'] = 'hamlet'
        else:
            node.tags['place'] = 'neighbourhood'
    for nom, position, angle in rues:
        node = osm_add_node(osm, cadastre_to_osm_transform(position))
        node.tags['name'] = nom
        node.tags['angle'] = str(int(round(angle * 180 / math.pi))) + u"°"
    OsmWriter(osm).write_to_stream(osm_output)


def args_fatal_error(cause):
    sys.stdout.write("ERREUR: %s \n" % cause)
    sys.stdout.write("USAGE: %s fichier.pdf+ [fichier.osm]\n" % sys.argv[0])
    sys.exit(-1)


def main(argv):
    if (len(argv) < 2): 
        args_fatal_error("fichier .pdf non spécifié")
    pdf_filename_list = sys.argv[1:]
    if pdf_filename_list[-1].endswith(".osm"):
        osm_output = open(pdf_filename_list.pop(),"w")
    else:
        osm_output = sys.stdout
    for f in pdf_filename_list:
        if (not f.endswith(".svg")) and (not f.endswith(".pdf")):
            args_fatal_error("l'argument n'est pas un fichier .pdf ou .svg: " + f)
        if not os.path.exists(f):
            args_fatal_error("fichier non trouvé: " + f)
        bboxfile = f[:-4] + ".bbox"
        if not os.path.exists(bboxfile):
            args_fatal_error("fichier .bbox correspondant non trouvé: " + bboxfile)
    pdf_vers_osm_noms(pdf_filename_list, osm_output)
    

if __name__ == '__main__':
    main(sys.argv)


