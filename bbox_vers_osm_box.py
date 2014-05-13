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


""" Convertie une liste de fichier .bbox en un fichier .osm.
Le fichier .osm contiendra une boite pour chaque fichier .bbox.
Cela peut aider sous JOSM à identifier de quel fichier .pdf ou .svg
original un élément provient.
"""


import sys
import time
import xml.parsers.expat
import os.path
from math  import *
from osgeo import osr    # apt-get install python-gdal
from pdf_vers_osm_housenumbers import Point,BoundingBox,Transform,CadastreToOSMTransform

def write_osm_for_boxes(output, osm_bbox, osm_boxes):
    output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    output.write("<osm version='0.6' generator='%s'>\n" % (sys.argv[0],))
    if osm_bbox:
        output.write("<bounds minlon='%f' minlat='%f' maxlon='%f' maxlat='%f' />\n" % 
                     (osm_bbox.x1, osm_bbox.y1, osm_bbox.x2,osm_bbox.y2))
    id = 0;
    for name, box in osm_boxes.iteritems():
        output.write("  <node id='%d' lon='%f' lat='%f'/>\n" % 
		(id-1, box.x1, box.y1))
        output.write("  <node id='%d' lon='%f' lat='%f'/>\n" % 
		(id-2, box.x2, box.y1))
        output.write("  <node id='%d' lon='%f' lat='%f'/>\n" % 
		(id-3, box.x2, box.y2))
        output.write("  <node id='%d' lon='%f' lat='%f'/>\n" % 
		(id-4, box.x1, box.y2))
        output.write("  <way id='%d'>\n" % (id-5))
        output.write("    <nd ref='%d'/>\n" % (id-1))
        output.write("    <nd ref='%d'/>\n" % (id-2))
        output.write("    <nd ref='%d'/>\n" % (id-3))
        output.write("    <nd ref='%d'/>\n" % (id-4))
        output.write("    <nd ref='%d'/>\n" % (id-1))
        output.write("    <tag k='name' v='%s'/>\n" % (name))
        output.write("    <tag k='area' v='yes'/>\n")
        output.write("  </way>\n")
        id = id - 5
    output.write("</osm>\n")

def bbox_vers_osm_box(bbox_filename_list, osm_output):
    osm_result_housenumbers = {}
    osm_result_bbox = None
    osm_boxes = {}
    for bbox_filename in bbox_filename_list:
        cadastre_code_IGNF_projection, cadastre_bbox = open(bbox_filename).read().split(":") 
        cadastre_bbox = BoundingBox(*[float(v) for v in cadastre_bbox.split(",")])
        cadastre_to_osm_transform = CadastreToOSMTransform(cadastre_code_IGNF_projection)
        osm_box = cadastre_to_osm_transform.transform_bbox(cadastre_bbox)
        osm_boxes[bbox_filename[:-5]] = osm_box
        if osm_result_bbox == None:
            osm_result_bbox = osm_box
        else:
            osm_result_bbox = osm_result_bbox.extend_to_bbox(osm_box)
    write_osm_for_boxes(osm_output, osm_result_bbox, osm_boxes)
    osm_output.flush()

def args_fatal_error(cause):
    sys.stdout.write("ERREUR: %s \n" % cause)
    sys.stdout.write("USAGE: %s fichier.bbox+ [fichier.osm]\n" % sys.argv[0])
    sys.exit(-1)

def main(argv):
    if (len(argv) < 2): 
        args_fatal_error("fichier .bbox non spécifié")
    bbox_filename_list = sys.argv[1:]
    if bbox_filename_list[-1].endswith(".osm"):
        osm_output = open(bbox_filename_list.pop(),"w")
    else:
        osm_output = sys.stdout
    for f in bbox_filename_list:
        if not f.endswith(".bbox"):
            args_fatal_error("l'argument n'est pas un fichier .bbox: " + f)
        if not os.path.exists(f):
            args_fatal_error("fichier non trouvé: " + f)
    bbox_vers_osm_box(bbox_filename_list, osm_output)
    

if __name__ == '__main__':
    main(sys.argv)


