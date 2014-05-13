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
    Cherche les buildings d'OSM et fusionne des noeuds adresses avec eux
    si ils sont près.
"""

import sys
import math
import os.path
import rtree.index
import itertools
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry.polygon import Polygon

import cadastre 
from osm import Osm, OsmParser, OsmWriter
from cherche_fantoir_et_osm_highways import open_osm_ways_commune
from cherche_fantoir_et_osm_highways import open_osm_multipolygon_s_ways_commune

MAX_BUILDING_DISTANCE_METERS = 2
NODE_INSIDE_BUILDING_DISTANCE_MARGIN = 0.1

def get_osm_buildings_and_barrier_ways(code_departement, code_commune):
    """ Retourne un objet Osm contenant tout les ways de la commune correspondant 
        au buildings et au barrier."""
    merge_osm = Osm({})
    input_osms = [
        open_osm_ways_commune(code_departement, code_commune, "building", nodes=True),
        open_osm_multipolygon_s_ways_commune(code_departement, code_commune, "building", nodes=True),
        open_osm_ways_commune(code_departement, code_commune, "barrier", nodes=True),
    ]
    for osm in input_osms:
      for id,node in osm.nodes.iteritems():
          if not id in merge_osm.nodes:
            merge_osm.add_node(node)
      for id, way in osm.ways.iteritems():
          if any([nid not in osm.nodes for nid in way.nodes]):
              # Il manque des nodes à ce way, ça arrive parfois
              # dans les résultats d'overpass, je ne sais pas pourquoi
              # mais cela ferait bugger l'utilisation de ce way
              # donc on le zap:
              continue
          if not id in merge_osm.ways:
            merge_osm.add_way(way)
      for id, rel in osm.ways.iteritems():
          if not id in merge_osm.relations:
            merge_osm.add_relation(rel)
    return merge_osm
    
def orthoprojection_on_segment_ab_of_point_c(a,b,c):
    """ Retourne la projection orthogonale du point c sur le segment [a,b],
        ou None si c n'est pas en face."""
    # http://www.codeguru.com/forum/printthread.php?t=194400
    xa,ya = a
    xb,yb = b
    xc,yc = c
    r_numerator = (xc-xa)*(xb-xa) + (yc-ya)*(yb-ya)
    r_denomenator = (xb-xa)*(xb-xa) + (yb-ya)*(yb-ya)
    if r_denomenator == 0:
        return a;
    r = r_numerator / r_denomenator;
    if r<0 or r>1:
        return None
    elif r == 0:
        return a
    elif r==1:
        return b
    else:
        x = xa + r*(xb-xa)
        y = ya + r*(yb-ya)
        return (x,y)

def cartesien_vers_polaire(x,y):
    r = math.sqrt(x*x+y*y)
    if r == 0:
        t = 0
    elif x > 0:
        t = math.atan(y/x)
    elif x < 0 and y >= 0:
        t = math.atan(y/x) + math.pi
    elif x < 0 and y < 0:
        t = math.atan(y/x) - math.pi
    elif x == 0 and y > 0:
        t = math.pi/2
    elif x == 0 and y < 0:
        t = - math.pi/2
    return (r,t)

def incidence(a, b, angle):
    """retourne l'incidence de l'angle par rapport au segment ab"""
    ax,ay = a
    bx,by = b
    _, ab_angle = cartesien_vers_polaire(bx - ax, by - ay)
    incidence = abs(math.pi/2 - ((angle - ab_angle) % math.pi))
    return incidence
    

def angle_projection_on_segment_ab_of_point_c(a,b,c,angle):
    """ Retourne la projection du point c sur le segment [a,b]
        en suivant la direction angle, ou None si le segment 
        n'est pas en face."""
    if a == b: 
        return None
    #http://scalion.free.fr/getinter.htm#paulbourke
    x1,y1 = a
    x2,y2 = b
    x3,y3 = c
    x4,y4 = x3 + math.cos(angle), y3 + math.sin(angle)
    r_numerator = (x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)
    r_denomenator = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if r_denomenator == 0:
        return None
    r = r_numerator / r_denomenator;
    if r<0 or r>1:
        return None
    elif r == 0:
        return a
    elif r==1:
        return b
    else:
        x = x1 + r*(x2-x1)
        y = y1 + r*(y2-y1)
        return (x,y)


def nearest_intersection(node, ways, ways_osm, angle = None):
    """Recherche l'intersection la plus proche entre le node et les ways donnés.
       Retourne un tuple (way, index, position) correspondant au way le plus proche,
       à l'index ou inserer le points d'entersection dans la liste des noeuds du way,
       et la position de cette intersection.
       Si l'angle est précisé, la distance sera calculée suivant cet angle,
       sinon une projection orthogonale vers le way sera effectuée.
    """
    best_square_distance = float("inf")
    best_way = None
    best_index = -1
    best_pos = (0,0)
    x,y = node.xy
    for way in ways:
        for i in xrange(len(way.nodes)-1):
            a = ways_osm.nodes[way.nodes[i]]
            b = ways_osm.nodes[way.nodes[i+1]]
            if angle != None:
                p = angle_projection_on_segment_ab_of_point_c(a.xy, b.xy, node.xy, angle)
            else:
                p = orthoprojection_on_segment_ab_of_point_c(a.xy, b.xy, node.xy)
            if p:
                px,py = p
                square_distance = (px-x)*(px-x) + (py-y)*(py-y)
                if square_distance < best_square_distance:
                    best_square_distance = square_distance
                    best_way = way
                    best_index = i+1
                    best_pos = p
    return best_way, best_index, best_pos

                

def distance_a_b((x1,y1),(x2,y2)):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

def cherche_osm_buildings_proches(code_departement, code_commune, osm, transform_to_osm, transform_from_osm):
    """ Cherche a intégrer les nœuds "addr:housenumber" du fichier
        d'entrée osm avec les building extraits de la base OSM.
    """
    sys.stdout.write((u"Intégration avec les buidings proches présent dans la base OSM.\n").encode("utf-8"))
    sys.stdout.write((u"Chargement des buidings\n").encode("utf-8"))
    sys.stdout.flush();
    buildings_osm = get_osm_buildings_and_barrier_ways(code_departement, code_commune)
    for node in itertools.chain.from_iterable(
            [o.nodes.itervalues() for o in [osm, buildings_osm]]):
        if not hasattr(node,'xy'):
            node.xy = transform_from_osm((float(node.attrs["lon"]), float(node.attrs["lat"])))
    # créé un index spatial de tous les ways:
    ways_index = rtree.index.Index()
    for way in buildings_osm.ways.itervalues():
        if way.nodes[0] == way.nodes[-1]:
            way.shape = Polygon([buildings_osm.nodes[id].xy for id in way.nodes])
        else:
            way.shape = LineString([buildings_osm.nodes[id].xy for id in way.nodes])
        ways_index.insert(way.id(), way.shape.bounds, way.id())
    sys.stdout.write((u"Recherche des buiding proches\n").encode("utf-8"))
    sys.stdout.flush();
    for node in osm.nodes.values():
        if "addr:housenumber" in node.tags:
            x,y = node.xy
            search_bounds = [x - MAX_BUILDING_DISTANCE_METERS, y - MAX_BUILDING_DISTANCE_METERS,
                             x + MAX_BUILDING_DISTANCE_METERS, y + MAX_BUILDING_DISTANCE_METERS]
            near_ways = [buildings_osm.ways[e.object] for e in ways_index.intersection(search_bounds, objects=True)]
            if  hasattr(node, 'limite_parcelle') and node.limite_parcelle != None:
                    #and node.liimite_parcelle.distance(node.xy) < MAX_BUILDING_DISTANCE_METERS:
                # On connais les limites de la parcelle 
                # On vas donc filtrer les ways avec ceux qui sont contenus
                # dans la parcelle.
                # Pour déterminer les ways qui sont contenus dans la parcelle
                # avec un peut de marge, on vas faire l'union de deux
                # tests:
                # - les way qui sont strictement contenus dans les limites de
                #   parcelle étendue d'1m (afin de considérer par exemple les  
                #   barier qui sont en limite de parcelle)
                # - les way qui intersect les limites réduite d'1m de la parcelle
                #   (afin de prendre en comte aussi les buidings à cheval sur 
                #    une autre parcelle).
                limite_etendue = node.limite_parcelle.buffer(1)
                limite_reduite = node.limite_parcelle.buffer(-1)
                near_ways = filter(lambda way:
                    limite_reduite.intersects(way.shape) or
                        limite_etendue.contains(way.shape),
                    near_ways)

            # Les numéros déssinés sur le cadastre sont souvent orientés
            # vers la parcelle ou le building auquel il font référence
            # Si se n'est pas le cas il seront dessinés horizontalement.
            # Donc pour les numéros qui ne sont pas horizontal (angle < -2° ou > 2°)
            # on vas chercher à les projeter selon leur angle.
            # Sinon, sans angle, la projection sera faite orthogonalement.
            angle = None
            if hasattr(node, "angle") and node.angle != None:
                angle_deg = node.angle*180 / math.pi
                if angle_deg < -2 or angle_deg > 2:
                    # on projete perpandiculairement (on ajoute 90°=pi/2)
                    angle = node.angle + math.pi/2

            best_way, best_index, best_pos = nearest_intersection(node, near_ways, buildings_osm, angle)




            if best_way and distance_a_b(node.xy, best_pos) < MAX_BUILDING_DISTANCE_METERS:
                # Il pourait en fait y avoir plusieurs ways qui contiennent le même segment, on vas tous les chercher
                # FIXME: il faudrait même chercher parmis les ways qui ne sont pas des building...
                a = best_way.nodes[best_index-1]
                b = best_way.nodes[best_index]
                p = Point(node.xy)
                best_ways = []
                best_indexes = []
                node_inside_building = False
                for way in near_ways:
                    for i in xrange(len(way.nodes)-1):
                        if (way.nodes[i] == a and way.nodes[i+1] == b) \
                                or (way.nodes[i] == b and way.nodes[i+1] == a):
                            best_ways.append(way)
                            best_indexes.append(i+1)
                            if type(way.shape) == Polygon \
                                    and way.shape.contains(p) \
                                    and way.shape.boundary.distance(p) > NODE_INSIDE_BUILDING_DISTANCE_MARGIN:
                                node_inside_building = True

                # Si on a projeté selon l'angle du numéro, on vérifie qu'il n'y a pas trop d'incidence 
                # pour la projection, l'idéal étant bien sure une projection
                # orthogonale cad avec une incidence nulle. On autorise jusqu'à 30°(pi/6):
                a_xy = buildings_osm.nodes[a].xy
                b_xy = buildings_osm.nodes[b].xy
                trop_d_incidence = angle != None and incidence(a_xy, b_xy, angle) > (math.pi/6)

                # On intègre pas le numéro si il est à l'intérieur d'un building,
                # car sur le cadastre un numéro dessiné dans un building est forcément mal placé
                if (not node_inside_building) and (not trop_d_incidence):
                    # Comme on vas ajouter node a un way provenant du fichier buildings_osm, 
                    # pour garder buildings_osm cohérent, on ajoute aussi node à buildings_osm:
                    buildings_osm.add_node(node)
                    for best_way,best_index in zip(best_ways, best_indexes):
                        # On ajoute les best_way et ses nodes au fichier osm:
                        for id in best_way.nodes:
                            if not id in osm.nodes:
                                osm.add_node(buildings_osm.nodes[id])
                        if not best_way.id() in osm.ways:
                            osm.add_way(best_way)
                        # On insère node au best way a la position best_index:
                        best_way.attrs["action"] = "modify"
                        best_way.nodes.insert(best_index, node.id())
                    # On déplace node à la position best_pos:
                    node.xy = best_pos
                    node.attrs["lon"], node.attrs["lat"] = map(str, transform_to_osm(best_pos))


#
#    
#def print_help():
#    programme = sys.argv[0]
#    spaces = " " * len(programme)
#    sys.stdout.write((u"Récupération des code fantoir et des highway OSM des associatedStreet\n").encode("utf-8"))
#    sys.stdout.write((u"USAGE:" + "\n").encode("utf-8"))
#    sys.stdout.write((u"%s  CODE_DEPARTEMENT CODE_COMUNE input.osm output.osm" % programme + "\n").encode("utf-8"))
#
#def command_line_error(message, help=False):
#    sys.stdout.write(("ERREUR: " + message + "\n").encode("utf-8"))
#    if help: print_help()
#
#
#def main(argv):
#    if len(argv) != 5 or argv[1] in ["-h","-help","--help"]:
#        print_help()
#        sys.exit()
#    code_departement = argv[1]
#    code_commune = argv[2]
#    input_filename = argv[3]
#    output_filename = argv[4]
#    if len(code_departement) != 3:
#        command_line_error("le code departement doit avoir 3 chiffres")
#    if len(code_commune) != 5:
#        command_line_error("le code commune doit avoir 5 lettres ou chiffres")
#    osm = OsmParser().parse(input_filename)
#    osm_noms = None
#    osm_noms_filename = code_commune + "-noms.osm"
#    if os.path.exists(osm_noms_filename):
#        print "Charges les noms depuis le fichier " + osm_noms_filename
#        osm_noms = OsmParser().parse(osm_noms_filename)
#    cherche_fantoir_et_osm_highways(code_departement, code_commune, osm, osm_noms)
#    OsmWriter(osm).write_to_file(output_filename)
#
#if __name__ == '__main__':
#    main(sys.argv)
#
