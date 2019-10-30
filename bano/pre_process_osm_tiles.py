#!/usr/bin/env python
# coding: UTF-8

# import sys
# import glob
import os,os.path

from datetime import date, timedelta

from pathlib import Path

# # from .core import load_cadastre_hsnr
# from .outils_de_gestion import batch_start_log
# from .outils_de_gestion import batch_end_log

# from . import db
# from . import helpers as hp
# from . import db_helpers as dh
from .models import Tile,Tiles

def save_INSEE_list(insee_list, insee_filename):
    with open(insee_filename,'w') as f:
        f.write('\n'.join(insee_list))


def process(**kwargs):
    tiles = Tiles()
    tiles_directory = Path(os.environ['EXPIRE_TILES_DIR']) / (date.today() - timedelta(1)).strftime('%Y%m%d')
    # print(tiles_directory)
    tilefiles = tiles_directory.glob('*.tiles')
    # print(list(tilefiles))
    for l in list(tilefiles):
        # print(l)
        tiles.add_tiles_from_file(l)
    # print(tiles.as_list_of_Box2D())
    save_INSEE_list(tiles.convert_to_insee_list(),'insee_update_osm.csv')

    # tile.as_PG_geom()
    # lire les fichiers de la veille
    # dedoublonner
    # convertir les tuiles en geom
    # charger en base
    # croiser insee
    # ecrire la liste