#!./venv37/bin/python
# -*- coding: utf-8 -*-

import glob
import os

from datetime import date, timedelta
from pathlib import Path

from . import db

from .models import Tile,Tiles

def get_csv_filename(source,dept):
    return f"{source}.{dept}.csv"

def get_bal_insee_list(source,dept):
    with db.bano_cache.cursor() as cur:
        cur.execute(f"SELECT DISTINCT commune_code FROM bal_{source} WHERE commune_code LIKE '{dept}%' ORDER BY 1;")
        return cur.fetchall()

def save_osm_insee_list(insee_list, insee_filename):
    with open(insee_filename,'w') as f:
        f.write('\n'.join(insee_list))

def get_osm_insee_list():
    tiles = Tiles()
    tiles_directory = Path(os.environ['EXPIRE_TILES_DIR']) / (date.today() - timedelta(1)).strftime('%Y%m%d')
    tilefiles = tiles_directory.glob('*.tiles')
    for l in list(tilefiles):
        print(f"Lecture de {l}")
        tiles.add_tiles_from_file(l)
    save_osm_insee_list(tiles.convert_to_insee_list(), get_source_csv_filename('osm'))

def save_bal_insee_list(dir,source,dept):
    with open(dir / get_csv_filename(source,dept),'w') as f:
        f.write('\n'.join([i[0] for i in (get_bal_insee_list(source,dept))]))

def set_csv_directory(dir):
    if not dir.exists():
        os.mkdir(dir)

def get_directory_pathname():
    return Path(os.environ['CSV_DIR'])

def compile_bal_insee_list(source,dir):
    with open(get_source_csv_filename(source),'w') as fw:
        for fr in sorted(glob.glob(f"{dir}/{source}.*.csv")):
            with open(fr) as fro:
                fw.write(fro.read()+'\n')
            Path.unlink(Path(fr))

def get_source_csv_filename(source):
    return get_directory_pathname() / f"insee_update_{source}.csv"

def get_target_csv_filename(source):
    return Path(os.environ['BANO_DIR']) / f"insee_{source}.csv"

def merge_bano_insee_lists(sources,target):
    insee_set = set()
    for s in sources :
        with open(get_source_csv_filename(s),'r') as sl:
            for l in sl:
                insee_set.add(l)
    with open(get_target_csv_filename(target),'w') as w:
        for s in sorted(insee_set):
            w.write(s)


def update_insee_lists(**kwargs):
    compile_bal_insee_list('cadastre',get_directory_pathname())
    compile_bal_insee_list('locales',get_directory_pathname())
    get_osm_insee_list()
    merge_bano_insee_lists(['cadastre','osm'],'cadastre')
    merge_bano_insee_lists(['locales','osm'],'locales')
    merge_bano_insee_lists(['osm'],'osm')
