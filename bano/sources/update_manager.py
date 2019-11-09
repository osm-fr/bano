#!./venv37/bin/python
# -*- coding: utf-8 -*-

import glob
import os
from pathlib import Path

from .. import db

def get_csv_filename(source,dept):
    return f"{source}.{dept}.csv"

def get_bal_insee_list(source,dept):
    with db.bano_cache.cursor() as cur:
        cur.execute(f"SELECT DISTINCT commune_code FROM bal_{source} WHERE commune_code LIKE '{dept}%' ORDER BY 1;")
        return cur.fetchall()

def save_insee_list(dir,source,dept):
    with open(dir / get_csv_filename(source,dept),'w') as f:
        f.write('\n'.join([i[0] for i in (get_bal_insee_list(source,dept))]))

def set_csv_directory(dir):
    if not dir.exists():
        os.mkdir(dir)

def get_directory_pathname():
    return Path(os.environ['CSV_DIR'])

def compile_insee_list(source,dir):
    with open(dir / f"{source}.csv",'w') as fw:
        for fr in sorted(glob.glob(f"{dir}/{source}.*.csv")):
            with open(fr) as fro:
                fw.write(fro.read()+'\n')
            Path.unlink(Path(fr))
            # with open(fr,'w') as frw:
            #     frw.write('')
            
