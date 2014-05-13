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


import os
import sys
import time
import math
import os.path
import traceback
import subprocess
import xml.parsers.expat
import xml.etree.ElementTree as ET
from math  import *
try:
  from osgeo import osr    # apt-get install python-gdal
except:
  traceback.print_exc()
  print "Please install python-gdal (sudo apt-get install python-gdal)"

from mytools import toposort

THIS_DIR = os.path.dirname(__file__)
REFERENCE_HOUSENUMBERS = os.path.join(THIS_DIR, "reference-housenumbers.svg")
SOURCE_TAG = u"cadastre-dgi-fr source : Direction Générale des Finances Publiques - Cadastre. Mise à jour : " + time.strftime("%Y")

class Point(object):
    """ An object with an x and a y field"""
    __slots__ = ('x','y')
    def __init__(self, x, y):
        assert type(x) == float
        assert type(y) == float
        self.x = x
        self.y = y
    def __len__(self):
        return 2
    def __getitem__(self, key):
        if key == 0: return self.x
        if key == 1: return self.y
        raise IndexError()
    def __str__(self):
        return str(self.x) + "," + str(self.y)
    def __repr__(self):
        return "Point(" + repr(self.x) + ", " + repr(self.y) + ")"
    def is_empty(self):
        return False

class BoundingBox(object):
    __slots__  = ("x1","y1","x2","y2")
    def __init__(self, x1,y1,x2,y2):
        self.x1 = min(x1,x2)
        self.y1 = min(y1,y2)
        self.x2 = max(x1,x2)
        self.y2 = max(y1,y2)
    def extend_to_bbox(self, bbox):
        x1 = min (self.x1, bbox.x1)
        y1 = min (self.y1, bbox.y1)
        x2 = max (self.x2, bbox.x2)
        y2 = max (self.y2, bbox.y2)
        return BoundingBox(x1,y1,x2,y2)
    def p1(self):
        return Point(self.x1, self.y1)
    def p2(self):
        return Point(self.x2, self.y2)
    def __getitem__(self, key):
        if key == 0: return self.x1
        if key == 1: return self.y1
        if key == 2: return self.x2
        if key == 3: return self.y2
        raise IndexError()
    def width(self):
        return self.x2 - self.x1
    def height(self):
        return self.y2 - self.y1
    def center(self):
        return Point((self.x1+self.x2)/2,
                     (self.y1+self.y2)/2)
    def is_point_inside(self, point):
        return (point.x >= self.x1) and (point.x <= self.x2) and \
               (point.y >= self.y1) and (point.y <= self.y2)
    def __str__(self):
        return "(" + str(self.x1) + ", " + str(self.y1) + ", "+ str(self.x2) + ", " + str(self.y2) + ")"
    def __repr__(self):
        return "Position(" + repr(self.x1) + ", " + repr(self.y1) + ", "+ repr(self.x2) + ", " + repr(self.y2) + ")"
    @staticmethod
    def of_points(points):
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return BoundingBox( min(xs), min(ys), max(xs), max(ys))


class Transform(object):
    def __init__(self):
        pass
    def transform_point(self, point):
        raise Exception("not implemented")
    def transform_points(self, points):
        return [self.transform_point(p) for p in points]
    def transform_bbox(self, bbox):
        p1 = self.transform_point(bbox.p1())
        p2 = self.transform_point(bbox.p2())
        return BoundingBox.of_points([p1,p2])

class CadastreToOSMTransform(Transform):
    """Transformation from IGNF coordinates used by the cadastre
       into coordinates used by OSM"""
    def __init__(self, cadastre_IGNF_code):
        Transform.__init__(self)
        source = osr.SpatialReference();
        target = osr.SpatialReference();
        source.ImportFromProj4(
            "+init=IGNF:" + cadastre_IGNF_code + " +wktext");
        target.ImportFromEPSG(4326);
        self.transformation = osr.CoordinateTransformation(
            source, target)
    def transform_point(self, point):
        x,y,z = self.transformation.TransformPoint(point[0], point[1], 0.0)
        return Point(x,y)

class OSMToCadastreTransform(Transform):
    """Transformation from cordinates used by OSM 
       to IGNF coordinates used by the cadastre"""
    def __init__(self, cadastre_IGNF_code):
        Transform.__init__(self)
        source = osr.SpatialReference();
        target = osr.SpatialReference();
        target.ImportFromProj4(
            "+init=IGNF:" + cadastre_IGNF_code + " +wktext");
        source.ImportFromEPSG(4326);
        self.transformation = osr.CoordinateTransformation(
            source, target)
    def transform_point(self, point):
        x,y,z = self.transformation.TransformPoint(point[0], point[1], 0.0)
        return Point(x,y)

class PDFToCadastreTransform(Transform):
    """Transformation from the coordinates used inside a PDF, into the coordinate of the cadastre"""
    def __init__(self, pdf_bbox, cadastre_bbox):
        Transform.__init__(self)
        Transform.__init__(self)
        self.pdf_bbox = pdf_bbox
        self.cadastre_bbox = cadastre_bbox
    def transform_point(self, point):
        return Point(
            self.cadastre_bbox.x1 + 
                (point[0] - self.pdf_bbox.x1) *
                    self.cadastre_bbox.width() / self.pdf_bbox.width(),
            self.cadastre_bbox.y1 + 
                (point[1] - self.pdf_bbox.y1) 
                    * self.cadastre_bbox.height() / self.pdf_bbox.height())

class CompositeTransform(Transform):
    """Composition of many transformations"""
    def __init__(self, *transforms):
        Transform.__init__(self)
        self.transforms = transforms
    def transform_point(self, point):
        for t in self.transforms:
            point = t.transform_point(point)
        return point
        

def peek(list):
    if len(list):
      return list[-1]
    else:
      return None


class Path(object):
    """ Representation d'un path falicitant la reconnaisance.
    Un path est composé de deux champs:
     - une chaîne représentant une liste de commandes
     - une liste de points (x,y)
    Les commandes peuvent être: 
         M : move (1 argument)
         L : line (1 argument)
         C : curve  (3 arguments)
         Q : quadratic  (2 arguments)
         Z : close  (0 argument)
    """
    __slots__ = ('commands','points','most_distant_point_index', 'angle_and_points_for_path_recognition', 'style', 'd')
    commands_argument_count = { 'M': 1, 'L':1, 'C':3, 'Q':2,'Z':0}
    def __init__(self, commands, points, style="", d=None):
        self.commands = commands
        self.points = points
        self.most_distant_point_index = None
        self.angle_and_points_for_path_recognition = {}
        self.style = style
        self.d = d
    def __str__(self):
        result = []
        i = 0
        for c in self.commands:
            result.append(c)
            for foo in range(Path.commands_argument_count[c]):
                result.append(str(self.points[i]))
                i = i + 1
        return "\n".join(result)
    def __repr__(self):
        return "Path(" + str(self) + ")"
    def bbox(self, i=None):
        # aproximation
        if i == None:
            return BoundingBox.of_points(self.points)
        else:
            return BoundingBox.of_points(self.points[:i])
    def p0_distance(self, i=None):
        if i == None: i = self.get_p0_most_distant_point_index()
        (x1, y1), (x2, y2) =  self.points[0], self.points[i]
        return sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
    def get_angle_and_points_for_path_recognition(self, i):
        """
            Move, rotate and scale the list of points in order to facilitate 
            recognition.
    
            The following transformations are applied:
            - We first move the points so that the first one be in (0,0),
            i.e. we move everypoints by (-x1,-y1)
            - Then we rotate and scale the points so that the i commes
              at position (1,0)
        """
        if i not in self.angle_and_points_for_path_recognition:
            x1,y1 = self.points[0] # le premier point
            x2, y2 = self.points[i] # le second point
            # le rayon = 
            r = sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))
            if (r == 0.0):
                self.points_for_path_recognition[i] = 0, self.points
            else:
                # l'angle:
                t = atan2( (y2-y1), (x2-x1))
                cosTbyR = cos(-t) / r
                sinTbyR = sin(-t) / r
                self.angle_and_points_for_path_recognition[i] = t, [
                    Point(
                        # move rotate and scale the coordinates:
                        cosTbyR * (x-x1) - sinTbyR * (y-y1),
                        sinTbyR * (x-x1) + cosTbyR * (y-y1))
                    for x,y in self.points ]
        return self.angle_and_points_for_path_recognition[i]

    def get_p0_most_distant_point_index(self):
        """ retourne l'index du point le plus distant du premier"""
        if self.most_distant_point_index == None:
            max_squaredist = 0
            max_i = 0
            x0,y0 = self.points[0]
            for i in range(1,len(self.points)):
                xi, yi =  self.points[i]
                squaredist = (xi-x0)*(xi-x0) + (yi-y0)*(yi-y0)
                if squaredist > max_squaredist:
                    max_squaredist = squaredist
                    max_i = i
            self.most_distant_point_index = max_i
        return self.most_distant_point_index
            
        
    #def is_similar_to(self, other, tolerance = 0.05):
    #    i = self.get_p0_most_distant_point_index()
    #    return self.commands == other.commands and \
    #        maxdiff(self.get_points_for_path_recognition(i), 
    #                other.get_points_for_path_recognition(i)) \
    #            <= tolerance

    def startswith(self, other, tolerance = 0.05, min_scale = 0.9, max_scale=1.1):
        if self.commands.startswith(other.commands):
            i = other.get_p0_most_distant_point_index()
            scale_factor = self.p0_distance(i) / other.p0_distance(i)
            if scale_factor >= min_scale and scale_factor <= max_scale:
              other_angle, other_points = other.get_angle_and_points_for_path_recognition(i)
              self_angle, self_points = self.get_angle_and_points_for_path_recognition(i)
              if maxdiff(self_points[:len(other.points)], other_points) < tolerance:
                  result = self_angle - other_angle
                  if result <= -math.pi:
                      result += 2*math.pi
                  elif result > math.pi:
                      result -= 2*math.pi
                  elif result == 0.0:
                      # renvoie quelque chose d'evalué à True proche de 0:
                      result = sys.float_info.min
                  return result
        return False

    @staticmethod
    def from_svg(d):
        """ Create a Path from a svg d string"""
        commands = []
        points = []
        tokens = [ t for t in Path.__svg_path_tokenizer(d)]
        tokens.reverse()
        current_point = Point(0.0, 0.0)
        while tokens:
            t = tokens.pop()
            if t in ['M','L']:
                while True:
                    points.append(Point(tokens.pop(), tokens.pop()))
                    commands.append(t) 
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
                    t = 'L' # M subsequent values becomes L
            elif t in ['m', 'l']:
                while True:
                    # convert to absolute:
                    points.append(Point(current_point.x + tokens.pop(), current_point.y + tokens.pop()))
                    commands.append(t.upper())
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
                    t = 'L' # M subsequent values becomes L
            elif t in ['H','h','V','v']:
                while True:
                    # convert to 'L'
                    if t == 'H':
                        points.append(Point(tokens.pop(), current_point.y))
                    elif t == 'h':
                        points.append(Point(current_point.x + tokens.pop(), current_point.y))
                    elif t == 'V':
                        points.append(Point(current_point.x, tokens.pop()))
                    elif t == 'v':
                        points.append(Point(current_point.x, current_point.y + tokens.pop()))
                    commands.append('L')
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t == 'C':
                while True:
                    for i in range(3):
                        points.append(Point(tokens.pop(), tokens.pop()))
                    commands.append('C')
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t == 'c':
                while True:
                    # convert to absolute
                    for i in range(3):
                        points.append(Point(current_point.x + tokens.pop(), current_point.y + tokens.pop()))
                    commands.append('C')
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t in ['S', 's']:
                while True:
                    if peek(commands) == 'C':
                        # the control point is the reflextion of the previous control point
                        previous_control_point = points[-2]
                        points.append(Point(
                            current_point.x - previous_control_point.x + current_point.x,
                            current_point.y - previous_control_point.y + current_point.y))
                    else:
                        # no previous control point, use the current point
                        points.append(Point(current_point.x, current_point.y))
                    for i in range(2):
                        if t == 'S':
                            points.append(Point(tokens.pop(), tokens.pop()))
                        else:
                            # Convert to absolute:
                            points.append(Point(
                                current_point.x + tokens.pop(),
                                current_point.y + tokens.pop()))
                    commands.append('C')
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t == 'Q':
                while True:
                    for i in range(2):
                        points.append(Point(tokens.pop(), tokens.pop()))
                    commands.append('Q')
                    #Path.__convert_last_quadratic_command_to_cubic(commands,points) 
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t == 'q':
                while True:
                    for i in range(2):
                        # Convert to absolute:
                        points.append(Point(
                            current_point.x + tokens.pop(),
                            current_point.y + tokens.pop()))
                    commands.append('Q')
                    #Path.__convert_last_quadratic_command_to_cubic(commands,points) 
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t in ['T', 't']:
                while True:
                    if peek(commands) == 'Q':
                        # the control point is the refextion of the previous control point
                        previous_control_point = points[-2]
                        points.append(Point(
                            current_point.x - previous_control_point.x + current_point.x,
                            current_point.y - previous_control_point.y + current_point.y))
                    else:
                        # no previous control point, use the current point
                        points.append(Point(current_point.x, current_point.y))
                    if t == 'T':
                        points.append(Point(tokens.pop(), tokens.pop()))
                    else:
                        # Convert to absolute:
                        points.append(Point(
                            current_point.x + tokens.pop(),
                            current_point.y + tokens.pop()))
                    commands.append('Q')
                    #Path.__convert_last_quadratic_command_to_cubic(commands,points) 
                    current_point = points[-1]
                    if type(peek(tokens)) != float: break
            elif t in ['A','a']:
                raise Exception("unsuported svg path command: " + str(t) + " : " + d)
            elif t in ['Z','z']:
                commands.append('Z')
                #pass
            else:
                raise Exception("invalid path " + str(t) + " : " + d)
        return Path("".join(commands), points, d=d)

    #@staticmethod
    #def __convert_last_quadratic_command_to_cubic(commands, points):
    #    """ inkscape utilisé pour éditer les paths à reconnaître transforme
    #        malheureusement toute les commandes quadratic en cubic
    #        on fait donc de même pour pour pouvoir reconnaitre les path.
    #        Formule trouvée ici:
    #        http://fontforge.org/bezier.html
    #    """
    #    assert(commands[-1] == 'Q')
    #    commands[-1] = 'C'
    #    QP0 = points[-3]
    #    QP1 = points[-2]
    #    QP2 = points[-1]
    #    CP0 = QP0
    #    CP1 = Point(QP0[0] + (QP1[0] - QP0[0]) * 2 / 3, QP0[1] + (QP1[1] - QP0[1]) * 2 / 3) # QP0 + 2/3 *(QP1-QP0)
    #    CP2 = Point(QP2[0] + (QP1[0] - QP2[0]) * 2 / 3, QP2[1] + (QP1[1] - QP2[1]) * 2 / 3) # QP2 + 2/3 *(QP1-QP2) 
    #    CP3 = QP2
    #    #points[-3] = CP0
    #    points[-2] = CP1
    #    points[-1] = CP2
    #    points.append(CP3)

    @staticmethod
    def __svg_path_tokenizer(d):
        i = 0
        while i < len(d):
            c = d[i]
            o = ord(c)
            if o in (32, 9, 10, 13,44):
                i = i + 1
            elif o >= 45 and o <= 57:
                j = i+1
                while j < len(d):
                    oj = ord(d[j])
                    if ((oj < 45) or (oj > 57)) and (oj != ord('e')): 
                        break
                    j = j + 1
                yield float(d[i:j])
                i = j
            elif c in ['M','L','H','V','C','S','Q','T','A','Z', 'm','l','h','v','c','s','q','t','a','z']:
                yield c
                i = i + 1
            else:
                raise Exception("invalid character in path data: chr(" 
                    + str(ord(d[i])) + ") = '" + d[i] + "' :  " + d)

def projection_point(angle, point):
    return math.cos(angle) * point[0] + math.sin(angle) * point[1]
def projections_points(angle, points):
    cosa = math.cos(angle)
    sina = math.sin(angle)
    return [cosa*p[0] + sina * p[1] for p in points]
def largeur_path(angle, path):
    positions = projections_points(angle, path.points)
    return max(positions) - min(positions)

def rapport_l2_sur_l1(path):
    """ Calcule le rapport entre le premier et le deuxième segment du path.
        Cela est utilisé en pratique pour distinguer le l minuscule du 
        I majuscule
    """
    def distance((x1,y1),(x2,y2)):
        return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))
    l1 = distance(path.points[0], path.points[1])
    l2 = distance(path.points[1], path.points[2])
    return  l2 / l1

class TextPathRecognizer(object):
    __slots__ = ('database', 'tolerance', 'min_scale', 'max_scale', 'styles', 'force_horizontal', 'angle_tolerance_deg', 'space_width')
    def __init__(self, tolerance, min_scale, max_scale, styles=[], force_horizontal = False, angle_tolerance_deg = 5):
        self.database = {}
        self.tolerance = tolerance
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.styles = styles
        self.force_horizontal = force_horizontal
        self.angle_tolerance_deg = angle_tolerance_deg 
        self.space_width = None
    def add(self, value, path, alternatives=[]):
        # On utilise le début de la commande du path comme 
        # index de la database:
        idx = path.commands[:path.commands.index('Z')]
        if not idx in self.database:
            self.database[idx] = []
        self.database[idx].append((value, path, alternatives))
    def save_to_svg(self, filename):
        f = open(filename,"w")
        f.write("""<?xml version="1.0"?>\n<svg
          xmlns="http://www.w3.org/2000/svg"
          xml:space="preserve"
          xmlns:svg="http://www.w3.org/2000/svg"
          height="1052.5"
          width="1488.75"
          version="1.1">
        """)
        f.write(u"<!-- inversion de l'axe Y pour remettre à l'endroit:\n<g transform='matrix(1,0,0,-1,0,0)'>-->\n".encode("utf-8"))
        for elems in self.database.itervalues():
            for value, path, _ in elems:
                f.write('    <path style="fill:#000000;fill-opacity:1;fill-rule:nonzero;stroke:none"\n d="')
                f.write(path.d)
                f.write('">\n')
                f.write("        <title>" + value + "</title>\n")
                f.write("    </path>\n")
        f.write("<!--</g>-->\n")
        f.write("</svg>\n")
        f.close()
    def load_from_svg(self, filename):
        """Charge les paths de référence pour la reconnaissance depuis un fichier SVG.
           La valeur associée à reconnaître est stockée dans le titre des paths."""
        root = ET.parse(filename).getroot()
        elems = []
        #sys.stdout.write((u"#Charge les path: " + os.path.basename(filename) + "\n").encode("utf-8"))
        for p in root.iter('{http://www.w3.org/2000/svg}path'):
            # La valeur à reconnaître pour le path est stockée dans le titre:
            title = p.find('{http://www.w3.org/2000/svg}title')
            if title != None:
                elems.append((title.text, Path.from_svg(p.get('d'))))
        if len(elems) == 0:
            raise Exception("Aucun path avec un titre (<title>) dans le fichier " + filename)
        # La façon de reconnaître le texte contenu dans un path consiste à
        # comparer le début du path avec chacun des éléments de référence
        # conterus dans la database jusqu'à en trouver un qui correspond,
        # puis reconnaître la suite du path.
        # Pour certains caratère, comme ceux avec accents (ex: é) le
        # début du path vas être le même que la version sans sans accent
        # (ex: e) donc il est important de comparer d'abord avec la version
        # la plus complexe des path pour reconnaître é avant e, sans quoi
        # un fois reconnus e, l'accent tout seul qui suit ne serait pas
        # reconnu.
        # On utilise un tri topologique pour prendre en compte ces dépendances.
        # Mais il y a un autre problème à traiter: celui des caractrès
        # différents qui sont représentés par un même path éqvivalent mais
        # avec un angle différent, c'est le cas du carctère u qui est un n
        # à l'envers ou de p et d.  On ne peut pas trier ces cas là (car
        # c'est une dépendance circulaire) mais on vas les traiter de
        # façon particulière, en enregistrant pour chacun d'eux la liste
        # des alternatives possibles qu'il faudra potentiellement 
        # considérer si on l'a reconnu.
        deps = { i:set() for i in xrange(len(elems))} 
        alternatives = [set() for i in xrange(len(elems))]
        for i in xrange(len(elems)-1):
          value_i, path_i = elems[i]
          for j in xrange(i+1,len(elems)):
            value_j, path_j = elems[j]
            if value_i != value_j:
                i_startswith_j = path_i.startswith(path_j, tolerance = self.tolerance, min_scale=self.min_scale, max_scale=self.max_scale)
                j_startswith_i = path_j.startswith(path_i, tolerance = self.tolerance, min_scale=self.min_scale, max_scale=self.max_scale)
                if i_startswith_j:
                    if j_startswith_i:
                      #alternatives[i].add(j)
                      #alternatives[j].add(i)
                      angle_deg = abs(int(round(i_startswith_j*180/math.pi)))
                      #sys.stdout.write((u"#caractère %s ~(%d°) %s\n" % (value_i, (angle_deg/2)*2, value_j)).encode("utf-8"))
                      if angle_deg < self.angle_tolerance_deg:
                            alternatives[i].add(j)
                      #if angle_deg < 5:
                      #    for v,p in [(value_i,path_i), (value_j,path_j)]:
                      #        print "  - %s  : p0_distance : %f" %(v, p.p0_distance())
                      #        print "         len(points) : %d" % len(p.points)
                      #        print "         l2 / l1 = %f" % rapport_l2_sur_l1(p)
                      #        #print str([(p.points[i][0]-p.points[i-1][0], p.points[i][1]-p.points[i-1][1]) for i in xrange(1, len(p.points))])
                    else:
                        #sys.stdout.write((value_i + " commence par " + value_j + "\n").encode("utf-8"))
                        deps[i].add(i)
                elif j_startswith_i:
                    #sys.stdout.write((value_j + " commence par " + value_i + "\n").encode("utf-8"))
                    deps[j].add(i)
        for i in toposort(deps):
            val, path = elems[i]
            alters = [elems[j] for j in alternatives[i]]
            self.add(val, path, alters)
        # Calcule la distance d'un espace comme la moité de la largeur moyenne des caractères:
        # en considérant que les caractères sont horizontal (angle = 0)
        largeur_moyenne = sum([largeur_path(0, path) for value,path in elems]) / len(elems)
        self.space_width = largeur_moyenne / 2
        #print "Largeur espaces = " + str(self.space_width)

    def recognize(self, path):
        if self.styles:
            path_styles = path.style.split(';')
            for s in self.styles:
                if not s in path_styles: return None
        original_path = path
        result = ""
        if self.force_horizontal:
            original_angle = 0.0
        else:
            original_angle = None
        previous_position = None
        while len(path.points):
            found = False
            idx = path.commands[:path.commands.find('Z')]
            if idx in self.database:
                for value, compare_path, alternatives in self.database[idx]:
                    startswith = path.startswith(compare_path, tolerance=self.tolerance, min_scale=self.min_scale, max_scale=self.max_scale)
                    if startswith:
                        angle = startswith
                        if original_angle != None:
                            diff_angle = abs(angle - original_angle) 
                            if diff_angle > math.pi:
                                diff_angle = abs(2*math.pi - diff_angle)
                            if (diff_angle * 180 / math.pi) > self.angle_tolerance_deg:
                                # Ce caractère est reconu mais pas avec le bon angle, on passe 
                                continue
                        else:
                            # Le premier caractère du path déterminera l'angle du mot
                            # PB: traiter les alternatives (par exemple un mot qui commence par u OU n il faut considérer les deux possibilitées,
                            # qui peuvent ếtre déterminer par l'angle.
                            # Au lieux d'analyser toutes les alternatives, on vérifie que la positions du point suivant dans le path sera bien
                            # en avant par rapport au caractère considéré courant.
                            # FIXME: il faudrait mieux analyser toutes les alternatives possibles et renvoyer la liste de celle qui on reconnu tout le path
                            positions = projections_points(angle,  path.points[:len(compare_path.points)])
                            if len(path.points) > len(compare_path.points):
                                mean_cur_position = sum(positions)/len(positions)
                                next_point_position = projection_point(angle, path.points[len(compare_path.points)])
                                if next_point_position < mean_cur_position:
                                    #sys.stdout.write((u"caractère rejeté: " + value + "\n").encode("utf-8"))
                                    # Le caractère suivant serait dérrière, on a pas du choisir le bon angle, c'est à dire 
                                    # le bon caractère à reconnaître, on continue pour en chercher un autre:
                                    continue
                            original_angle = angle
                            #result = result + "angle(%.2f)" % (original_angle*180/math.pi)
                        if len(alternatives):
                            # Il y a des alternatives pour ce caractère, on vas utiliser le rapport_l2_l1 pour les
                            # départager
                            # NOTE: cela est fait en pratique uniquement pour distinguer le l minuscule du I majuscule
                            cur_rapport_l2_sur_l1 = rapport_l2_sur_l1(path)
                            compare_raport_l1_l2 = rapport_l2_sur_l1(compare_path)
                            for alt_value, alt_path in alternatives:
                                alt_rapport_l2_sur_l1 = rapport_l2_sur_l1(alt_path)
                                if abs(cur_rapport_l2_sur_l1-alt_rapport_l2_sur_l1) < abs(cur_rapport_l2_sur_l1-compare_raport_l1_l2):
                                    value = alt_value
                                    compare_raport_l1_l2 = alt_rapport_l2_sur_l1
                        # Calcule de la position des points por déterminer si il y a un espace
                        positions = projections_points(original_angle,  path.points[:len(compare_path.points)])
                        if previous_position != None:
                            distance = min(positions) - previous_position
                        else:
                            distance = 0
                        previous_position = max(positions)
                        #result = result + "loc[%.2f,%.2f] pos[%.2f .. %.2f]" % (path.points[0][0], path.points[0][1], min(positions), max(positions))
                        #result = result + (" distance(%.2f)" % distance)
                        if distance > self.space_width:
                            result = result + " "
                        result = result + value 
                        #result = result + ("(%.1f)" % (angle*180/math.pi))
                        # Maintenant on traite la suite du path:
                        path = Path(
                            path.commands[len(compare_path.commands):],
                            path.points[len(compare_path.points):])
                        found = True
                        break;
            if not found:
                break
        if result:
            if len(path.points):
                # On a pas tout reconnu
                result += "???"
            position = original_path.bbox().center()
            return result, position, original_angle
        else:
            return None

                    
def maxdiff(points1, points2):
    return max(
        [ max((abs(points1[i][0] - points2[i][0]),
               abs(points1[i][1] - points2[i][1])))
          for i in xrange(len(points1))])


class CadastreParser(object):
    """ Parse un fichier PDF obtenue depuis le cadastre,
        pour y trouver les <path> 
        Les path qui nous intéressent sont tous dans le même groupe <g>,
        donc on ignore completement les transformations de
        coordonées (pdf transform).
    """
    def __init__(self, path_handlers = None):
        self.path_handlers = path_handlers if path_handlers else []
    def add_path_handler(self, path_handler):
        self.path_handlers.append(handler)
    def parse(self, filename):
        bbox_filename = os.path.splitext(filename)[0]  + ".bbox"
        self.cadastre_projection, cadastre_bbox = open(bbox_filename).read().split(":")
        self.cadastre_bbox = BoundingBox(*[float(v) for v in cadastre_bbox.split(",")])
        self.pdf_bbox = None

        ext = os.path.splitext(filename)[1]

        if ext == ".svg":
            parser = xml.parsers.expat.ParserCreate()
            parser.StartElementHandler = self.handle_start_element
            parser.ParseFile(open(filename))
        elif ext == ".pdf":
            pipe = subprocess.Popen([
                    os.path.join(THIS_DIR, "pdfparser", "pdfparser"), 
                    filename], 
                    bufsize=128*1024, stdout=subprocess.PIPE).stdout
            while True:
                line = pipe.readline()
                if not line:
                    break
                path = Path.from_svg(line.rstrip())
                path.style = pipe.readline().rstrip()
                self.handle_path(path)
        else:
            raise Exception("not a pdf or svg filename: " + filename)

    def handle_start_element(self, name, attrs):
        name = name.lower()
        if name.lower() == "path":
            path = Path.from_svg(attrs["d"])
            if "style" in attrs:
                path.style = attrs["style"].replace(" ","")
            self.handle_path(path)

    def handle_path(self, path):
        if self.pdf_bbox == None:
            # Try to find the bbox (a white rectangle)
            if (path.commands == "MLLLLZ"
                    and "fill:#ffffff" in path.style.split(";")):
                self.pdf_bbox = path.bbox()
                self.pdf_to_cadastre_transform = PDFToCadastreTransform(self.pdf_bbox, self.cadastre_bbox).transform_point
                #sys.stdout.write("pdf bbox:" + str(self.bbox) + "\n")
        else:          
            for path_handler in self.path_handlers:
                if path_handler(path, self.pdf_to_cadastre_transform):
                    break


def write_osm_for_housenumbers(output, osm_bbox, housenumbers):
    #osm_bbox = BoundingBox.of_points(housenumbers.keys())
    output.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    output.write("<osm version='0.6' generator='%s' upload='false'>\n" % (sys.argv[0],))
    id = 0;
    for number, position, angle in housenumbers:
        id = id-1;
        output.write("  <node id='%d' lon='%f' lat='%f'>\n" % 
                     (id, position.x, position.y))
        output.write("    <tag k='addr:housenumber' v='%s' />\n" 
                     % (number,))
        output.write(("    <tag k='source' v='" + SOURCE_TAG + "'' />\n").encode("utf-8"))
        output.write(u"    <tag k='fixme' v='À vérifier et associer à la bonne rue' />\n".encode("utf-8"))
        output.write("  </node>\n")
    output.write("</osm>\n")


class HousenumberPathRecognizer(TextPathRecognizer):
    def __init__(self):
        TextPathRecognizer.__init__(self, tolerance=0.05, min_scale=0.8, max_scale=1.2, styles=["fill:#000000"])
        self.load_from_svg(REFERENCE_HOUSENUMBERS)
        self.housenumbers = []
    def handle_path(self, path, transform):
        found = self.recognize(path)
        if found:
            text, position, angle = found
            if text[0] in ["1","2","3","4","5","6","7","8","9"]:
                self.housenumbers.append((text, transform(position), angle))
                return text.find("???") == -1
        return False

        

def pdf_vers_cadastre_housenumbers(pdf_filename_list):
    housenumber_recognizer = HousenumberPathRecognizer()
    cadastre_parser = CadastreParser([housenumber_recognizer.handle_path])
    for pdf_filename in pdf_filename_list:
        cadastre_parser.parse(pdf_filename)
    return cadastre_parser.cadastre_projection, housenumber_recognizer.housenumbers

def pdf_vers_osm_housenumbers(pdf_filename_list, osm_output):
    cadastre_projection, cadastre_housenumbers = \
            pdf_vers_cadastre_housenumbers(pdf_filename_list)
    cadastre_to_osm_transform = CadastreToOSMTransform(cadastre_projection).transform_point
    osm_housenumbers = [
        (value, cadastre_to_osm_transform(position),angle) for (value, position,angle) in
          cadastre_housenumbers]
    write_osm_for_housenumbers(osm_output, None, osm_housenumbers)
    osm_output.flush()

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
    pdf_vers_osm_housenumbers(pdf_filename_list, osm_output)
    

if __name__ == '__main__':
    main(sys.argv)


