#!/usr/bin/env python

import csv
import os
import sys
import subprocess

from pathlib import Path

from . import constants, db
from . import helpers as hp

class Dataset:
    def __init__(self, dept):
        self.dept = dept
        self.query = self.get_query()
        self.data = None

    def get_query(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/export_dept.sql'),'r') as fq:
            return fq.read().replace('__dept__',self.dept)

    def get_data(self):
        with db.bano.cursor() as cur:
            cur.execute(self.query)
            return [d[0:-1] for d in cur.fetchall()]

    def get_target_filename(self,filetype):
        return f'bano-{self.dept}.{filetype}'

    def get_sas_full_filename(self,filetype):
        return Path(os.environ['EXPORT_SAS_DIR']) / self.get_target_filename(filetype)

    def get_webdir_full_filename(self,filetype):
        return Path(os.environ['EXPORT_WEB_DIR']) / self.get_target_filename(filetype)

    def save_as_csv(self):
        if not self.data :
            self.data = self.get_data()
        with open(self.get_sas_full_filename('csv'),'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data)

    def save_as_ttl(self):
        if not self.data :
            self.data = self.get_data()

    def save_as_shp(self):
        subprocess.run(['ogr2ogr', '-f',"ESRI Shapefile", '-lco', 'ENCODING=UTF-8', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:4326', '-overwrite', self.get_sas_full_filename('shp'), 'PG:dbname=cadastre user=cadastre', '-sql', f'{self.query}'])

    def move_to_web_directory(self):
        return True

def process(departements, **kwargs):
    for dept in departements:
        if not hp.is_valid_dept(dept):
            print(f"Code {dept} invalide pour un département - abandon")
            continue
        d = Dataset(dept)
        d.save_as_shp()
        d.save_as_csv()
        d.save_as_ttl()
        d.move_to_web_directory()
