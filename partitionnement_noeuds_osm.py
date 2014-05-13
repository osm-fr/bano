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

# Partitionne les noeuds d'un fichier osm en groupes de taille équivalente.

import sys
import time
import xml.parsers.expat
import os.path
import zipfile
import math
import bbox_vers_osm_box
from numpy import vstack
from scipy.cluster.vq import kmeans,vq
from cStringIO import StringIO

from osm import *
from pdf_vers_osm_housenumbers import BoundingBox


def partitionnement_points(points, nb_partitions):
  """ partitionnement de l'ensemble des points  
      en utilisant K-means de la bibliothèque scipy
      retourne un tableau qui donne l'index de la partition de chaque point
  """
  # Génère une matrice à partire des points:
  data = vstack((points,)) 
  # Calcule des partitions K-means avec K=nb_clusters
  centroids,_ = kmeans(data, nb_partitions)
  # Affecte chaque points dans une partition:
  idx,_ = vq(data,centroids)
  return idx

def partitionnement_osm_nodes(osm_nodes, taille_partitions):
  """  Partitionne une liste de noeuds osm en groupe de taille donnée.
       Retourne la liste des groupes.
  """
  try:
      # si on a gardé dans le champ xy la position des points dans la projection originale, on l'utilise:
      positions = [n.xy for n in osm_nodes]
  except:
      # sinon on utilise lon,lat:
      positions = [(float(n.attrs["lon"]), float(n.attrs["lat"])) for n in osm_nodes]
  nb_partitions = len(osm_nodes) / taille_partitions
  idx = partitionnement_points(positions , nb_partitions)
  partitions = [[] for p in xrange(nb_partitions)]
  bboxes = [(float("inf"),float("inf"),float("-inf"),float("-inf")) for p in xrange(nb_partitions)]
  for n in xrange(len(osm_nodes)):
    p = idx[n]
    partitions[p].append(osm_nodes[n])
    bboxes[p] = tuple(min(*m) for m in zip(bboxes[p][:2],positions[n])) + tuple(max(*m) for m in zip(bboxes[p][2:],positions[n]))
  return zip(partitions, bboxes)

def args_fatal_error(cause):
    sys.stdout.write("ERREUR: %s \n" % cause)
    sys.stdout.write("USAGE: %s input.osm  [taille [output.zip]]\n" % sys.argv[0])
    sys.exit(-1)

def main(argv):
    if (len(sys.argv) < 2): 
        args_fatal_error("fichier .osm non spécifié")
    input_filename = sys.argv[1]
    input_basename = os.path.splitext(os.path.basename(input_filename))[0]
    if len(sys.argv) < 3:
      taille = 50
    elif not (sys.argv[2].isdigit()): 
        args_fatal_error("format taille invalide")
    else:
      taille = int(sys.argv[2])
    if len(sys.argv) >= 4:
      output_filename = sys.argv[3]
    else:
      output_filename = os.path.splitext(input_filename)[0] + ("-partitionnement%d.zip" % taille)
    if len(sys.argv) > 4:
        args_fatal_error("trop d'arguments")
    print "Lecture de " + input_filename
    input_osm = OsmParser().parse(input_filename)
    input_bbox = input_osm.bbox()
    if len(input_osm.ways) > 0 or len(input_osm.relations) > 0:
      args_fatal_error("le fichier %s ne contient pas que des noeuds" % input_filename)
    print "Partitionnement...";
    if (len(input_osm.nodes) > taille):
      partitions = partitionnement_osm_nodes(input_osm.nodes.values(), taille)
    else:
      partitions = [(input_osm.nodes.values(), input_bbox),]
    print " -> %d partitions" % (len(partitions))
    print "Écriture de " + output_filename
    zip_output = zipfile.ZipFile(output_filename,"w", zipfile.ZIP_DEFLATED)
    taille_index = int(math.ceil(math.log10(len(partitions))))
    bboxes = {}
    for i in xrange(len(partitions)):
      nodes, bbox = partitions[i]
      p_name = ("partition_%%0%dd" % taille_index) % i
      bboxes[p_name] = BoundingBox(*bbox)
      p_osm = Osm(input_osm.attrs.copy())
      map(p_osm.add_node, nodes)
      s = StringIO()
      OsmWriter(p_osm).write_to_stream(s)
      zip_output.writestr(input_basename + "-" + p_name + ".osm", s.getvalue())
    s = StringIO()
    bbox_vers_osm_box.write_osm_for_boxes(s, BoundingBox(*input_bbox), bboxes)
    zip_output.writestr(input_basename + "-index.osm", s.getvalue())
    zip_output.close()
    

if __name__ == '__main__':
    main(sys.argv)


