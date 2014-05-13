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



""" Conversion pdf en svg en utilisant inkscape """

import sys
import os.path
import svg_sans_groupes


def pdf_vers_svg(pdf_filename):
    svg_filename = os.path.splitext(pdf_filename)[0] + ".svg"
    if not (os.path.exists(svg_filename) and os.path.exists(svg_filename + ".ok") and (os.path.getmtime(svg_filename) > os.path.getmtime(pdf_filename))):
        if os.path.exists(svg_filename + ".ok"): os.remove(svg_filename + ".ok")
        svg_sans_groupes_filename = os.path.splitext(pdf_filename)[0] + "-sans_groupes.svg"
        cmd = 'inkscape --without-gui' \
            + ' "--file=' + pdf_filename + '"'\
            + ' "--export-plain-svg=' + svg_filename + '"'
        sys.stdout.write(cmd + "\n")
        sys.stdout.flush()
        if os.system(cmd) != 0:
          raise Exception("impossible d'exécuter inkscape")
        # Crée une version du fichier sans groupes:
        svg_sans_groupes.SVG_G_Filter().parse(open(svg_filename), open(svg_sans_groupes_filename,"w"))
        open(svg_filename + ".ok", 'a').close()
    return svg_filename

def pdfs_vers_svgs(pdf_filename_list):
    return [pdf_vers_svg(pdf) for pdf in pdf_filename_list]

def print_help():
    programme = sys.argv[0]
    sys.stdout.write(u"Conversion pdf en svg" + "\n")
    sys.stdout.write(u"USAGE: %s fichier.pdf [fichier2.pdf ...]\n" % (programme,))

def command_line_error(message, help=False):
    sys.stdout.write("ERREUR: " + message + "\n")
    if help: print_help()


def main(argv):
    if len(argv) <= 1: 
        command_line_error("pas asser d'argument", True)
    elif argv[1] in ["-h", "-help","--help"]:
        print_help()
    else:
        pdf_filename_list = sys.argv[1:]
        for f in pdf_filename_list:
            if not f.endswith(".pdf"):
                command_line_error("l'argument n'est pas un fichier .pdf: " + f)
                return
        pdfs_vers_svgs(pdf_filename_list)

if __name__ == '__main__':
    main(sys.argv)

