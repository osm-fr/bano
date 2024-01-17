#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gzip
import tarfile
import os

from glob import glob
from shutil import copy2
from pathlib import Path

from .constants import DEPARTEMENTS
from . import helpers as hp
from . import batch as b

def get_source_dir():
    try:
        cwd = Path(os.environ['EXPORT_SAS_DIR'])
    except KeyError:
        raise ValueError(f"La variable EXPORT_SAS_DIR n'est pas définie")
    return cwd

def get_dest_dir():
    try:
        cwd = Path(os.environ['EXPORT_WEB_DIR'])
    except KeyError:
        raise ValueError(f"La variable EXPORT_WEB_DIR n'est pas définie")
    return cwd

def get_source_file(dept,extension):
    return Path(get_source_dir()) / f'bano-{dept}.{extension}'

def get_dest_file(dept,filetype,gzip=False,tar=False):
    ext = ".tar" if tar else ''
    ext = ext+".gz" if gzip else ext
    return Path(get_dest_dir()) / f'bano-{dept}.{filetype}{ext}'

def get_dest_file_full(filetype,gzip=False):
    gz_ext = '.gz' if gzip else ''
    return Path(get_dest_dir()) / f'full.{filetype}{gz_ext}'

def publish_as_shp(dept):
    id_batch = b.batch_start_log("publish SHP", "", dept)
    try :
        with tarfile.open(get_dest_file(dept, 'shp', True,True), "w:gz") as tar:
            tar.add(get_source_file(dept,'shp'), arcname=f'bano-{dept}.shp')
            tar.add(get_source_file(dept,'dbf'), arcname=f'bano-{dept}.dbf')
            tar.add(get_source_file(dept,'shx'), arcname=f'bano-{dept}.shx')
            tar.add(get_source_file(dept,'prj'), arcname=f'bano-{dept}.prj')
            tar.add(get_source_file(dept,'cpg'), arcname=f'bano-{dept}.cpg')
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def publish_as_csv(dept):
    id_batch = b.batch_start_log("publish CSV", "", dept)
    try :
        copy2(get_source_file(dept,'csv'),get_dest_dir())
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def publish_as_full_csv():
    id_batch = b.batch_start_log("publish FULL CSV", "", 'France')
    try:
        with gzip.open(get_dest_file_full('csv',True),'wb') as gz:
            for infile in sorted(glob(f'{get_source_dir()}/bano-*.csv')):
                with open(infile,'rb') as js:
                    gz.write(js.read())
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def publish_as_ttl(dept):
    id_batch = b.batch_start_log("publish TTL", "", dept)
    try :
        with gzip.open(get_dest_file(dept,'ttl',True,False),'wb') as gz:
            with open(get_source_file(dept,'ttl'),'rb') as ttl:
                gz.write(ttl.read())
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def publish_as_json(dept):
    id_batch = b.batch_start_log("publish JSON", "", dept)
    try :
        with gzip.open(get_dest_file(dept,'json',True,False),'wb') as gz:
            with open(get_source_file(dept,'json'),'rb') as js:
                gz.write(js.read())
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def publish_as_full_json():
    id_batch = b.batch_start_log("publish FULL JSON", "", 'France')
    try:
        with gzip.open(get_dest_file_full('sjson',True),'wb') as gz:
            for infile in sorted(glob(f'{get_source_dir()}/bano-*.json')):
                with open(infile,'rb') as js:
                    gz.write(js.read())
        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)

def process(departements, **kwargs):
    for dept in departements:
        if not hp.is_valid_dept(dept):
            print(f"Code {dept} invalide pour un département - abandon")
            continue
        publish_as_shp(dept)
        publish_as_csv(dept)
        publish_as_ttl(dept)
        publish_as_json(dept)

def process_full(**kwargs):
    publish_as_full_csv()
    publish_as_full_json()
