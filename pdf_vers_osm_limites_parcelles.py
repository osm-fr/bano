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
import sys
import time
import os.path

from osm import Osm,Node,Way,OsmWriter
from pdf_vers_osm_housenumbers import CadastreParser
from pdf_vers_osm_housenumbers import CadastreToOSMTransform


# distance max en mètres pour considérer qu'un polygon est fermé:
TOLERANFCE_FERMETURE_POLYGON_METRES = 0.5

class ParcellePathRecognizer(object):
  def __init__(self):
      self.commands_re = re.compile("^(MLLLL*Z)+$")
      self.parcelles = []
  def handle_path(self, path, transform):
      #style="fill:none;stroke:#000000;stroke-width:0.76063001;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:10;stroke-opacity:1;stroke-dasharray:none"
      if self.commands_re.match(path.commands) and path.style:
          style = dict([v.split(':') for v in path.style.split(';')])
          if (style.get('fill') == "none") and \
                  (style.get('stroke') == "#000000") and \
                  (style.get('stroke-opacity') == "1") and \
                  (style.get('stroke-dasharray') == "none") and \
                  style.has_key('stroke-width'):
              stroke_width = float(style["stroke-width"])
              if stroke_width > 0.7 and stroke_width < 0.8:
                  # dans certasns cas path le path ne correspond pas à une limite de parcelle, mais
                  # a une fleche qui fait le lien entre la parcelle et sont label, dans ce cas la
                  # la flèche n'est pas un polygone fermé, donc on ne garde que les polygones fermés
                  # dans le cas de limites imbriqués, il vas y avoir plusieurs limites
                  # différents dans le meme path, on découpe donc chaque polygones:
                  points = map(transform, path.points)
                  linear_rings = []
                  for commands_ring in path.commands[:-1].split('Z'):
                        first = points[0]
                        last = points[len(commands_ring)-1]
                        if max(abs(first[0]-last[0]), abs(first[1]-last[1])) \
                                < TOLERANFCE_FERMETURE_POLYGON_METRES: 
                            linear_rings.append(points[:len(commands_ring)])
                        else:
                            # Ce n'est pas un polygone fermé mais une ligne 
                            # brisée, probablement une flèche entre le numéro
                            # d'une petite parcelle et sa position
                            break
                        points = points[len(commands_ring):]
                  if len(linear_rings) > 0:
                      self.parcelles.append(linear_rings)
                      ##Polygon(linear_rings[0], linear_rings[1:]))
                      return True
      return False

def pdf_vers_limites_parcelles(pdf_filename_list):
    parcelle_path_recognizer = ParcellePathRecognizer()
    cadastre_parser = CadastreParser([parcelle_path_recognizer.handle_path])
    for pdf_filename in pdf_filename_list:
        cadastre_parser.parse(pdf_filename)
    parcelles = parcelle_path_recognizer.parcelles
    sys.stdout.write(str(len(parcelles)) +  " limites de parcelles\n")
    sys.stdout.flush()
    return cadastre_parser.cadastre_projection, parcelles

def pdf_vers_osm_limites_parcelles(pdf_filename_list, osm_output):
    projection, parcelles = pdf_vers_limites_parcelles(pdf_filename_list)
    cadastre_to_osm_transform = CadastreToOSMTransform(projection)
    osm = Osm({'upload':'false'})
    for parcelle in parcelles:
        #for linear_ring in list(polygon.interiors) + [polygon.exterior]:
        for linear_ring in parcelle:
            points = map(cadastre_to_osm_transform.transform_point, linear_ring)
            nodes = [Node({'lon':str(p.x), 'lat':str(p.y)}) for p in points]
            way = Way({})
            for n in nodes: 
                osm.add_node(n)
                way.add_node(n)
            osm.add_way(way)
    OsmWriter(osm).write_to_stream(osm_output)


def args_fatal_error(cause):
    sys.stdout.write("ERREUR: %s \n" % cause)
    sys.stdout.write("USAGE: %s fichier.svg+ [fichier.osm]\n" % sys.argv[0])
    sys.exit(-1)


def main(argv):
    if (len(argv) < 2): 
        args_fatal_error("fichier .svg non spécifié")
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
    pdf_vers_osm_limites_parcelles(pdf_filename_list, osm_output)
    

if __name__ == '__main__':
    main(sys.argv)


