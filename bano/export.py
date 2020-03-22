#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import os
import sys
import subprocess

from pathlib import Path

from . import constants, db
from . import helpers as hp

class Dataset:
    def __init__(self, dept):
        self.dept = dept
        self.csv_query = self.get_csv_query()
        self.csv_data = None
        self.json_commune_query = self.get_json_commune_query()
        self.json_commune_data = None
        self.json_voies_rapprochees_query = self.get_json_voies_rapprochees_query()
        self.json_voies_rapprochees_data = None
        self.json_voies_non_rapprochees_query = self.get_json_voies_non_rapprochees_query()
        self.json_voies_non_rapprochees_data = None

    def get_csv_query(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/export_csv_dept.sql'),'r') as fq:
            return fq.read().replace('__dept__',self.dept)

    def get_csv_data(self):
        with db.bano.cursor() as cur:
            cur.execute(self.csv_query)
            return [d[0:-1] for d in cur.fetchall()]

    def get_json_commune_query(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/export_json_dept_communes.sql'),'r') as fq:
            return fq.read().replace('__dept__',self.dept)

    def get_json_commune_data(self):
        with db.bano.cursor() as cur:
            cur.execute(self.json_commune_query)
            return cur.fetchall()

    def get_json_voies_non_rapprochees_query(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/export_json_dept_voies_non_rapprochees.sql'),'r') as fq:
            return fq.read().replace('__dept__',self.dept)

    def get_json_voies_non_rapprochees_data(self):
        with db.bano.cursor() as cur:
            cur.execute(self.json_voies_rapprochees_query)
            return cur.fetchall()

    def get_json_voies_rapprochees_query(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/export_json_dept_voies_rapprochees.sql'),'r') as fq:
            return fq.read().replace('__dept__',self.dept)

    def get_json_voies_rapprochees_data(self):
        with db.bano.cursor() as cur:
            cur.execute(self.json_voies_rapprochees_query)
            return cur.fetchall()

    def get_target_filename(self,filetype):
        return f'bano-{self.dept}.{filetype}'

    def get_sas_full_filename(self,filetype):
        return Path(os.environ['EXPORT_SAS_DIR']) / self.get_target_filename(filetype)

    def get_webdir_full_filename(self,filetype):
        return Path(os.environ['EXPORT_WEB_DIR']) / self.get_target_filename(filetype)

    def save_as_csv(self):
        if not self.csv_data :
            self.csv_data = self.get_csv_data()
        with open(self.get_sas_full_filename('csv'),'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.csv_data)

    def save_as_ttl(self):
        if not self.csv_data :
            self.csv_data = self.get_csv_data()

    def save_as_shp(self):
        subprocess.run(['ogr2ogr', '-f',"ESRI Shapefile", '-lco', 'ENCODING=UTF-8', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:4326', '-overwrite', self.get_sas_full_filename('shp'), 'PG:dbname=cadastre user=cadastre', '-sql', f'{self.csv_query}'])

    def save_as_json(self):
        if not self.json_commune_data :
            self.json_commune_data = self.get_json_commune_data()
        if not self.json_voies_non_rapprochees_data :
            self.json_voies_non_rapprochees_data = self.get_json_voies_non_rapprochees_data()
        if not self.json_voies_rapprochees_data :
            self.json_voies_rapprochees_data = self.get_json_voies_rapprochees_data()

            # print(self.json_commune_data[1])
        with open(self.get_sas_full_filename('json'),'w') as jsonfile:
            for id,type,name,cp,lat,lon,cityname,dept,region,population,adm_weight,importance,*others in self.json_commune_data:
                # jsonfile.write(json.dumps({"id": id,"type": type,"name": name,"postcode":cp,"lat": float(lat),"lon": float(lon),"city":cityname,"departement":dept,"region":region,"population":population,"adm_weight":adm_weight,"importance":float(importance)}))
                jsonfile.write(f'"id": {id}, "type": {type}, "name": {name}, "postcode": {cp}, "lat": {lat}, "lon": {lon}, "city": {cityname}, "departement": {dept}, "region": {region}, "population": {population}, "adm_weight": {adm_weight}, "importance": {importance}')
            for fantoir,citycode,type,name,postcode,lat,lon,city,departement,region,importance,housenumbers,*others in self.json_voies_non_rapprochees_data:
                s_housenumbers = ','.join([f'"{s.split("$")[0]}":{{"lat":{s.split("$")[1]},"lon":{s.split("$")[2]}}}' for s in housenumbers.split('#') ])
                jsonfile.write(f'{{"id":"{fantoir}","citycode":"{citycode}","type":"{type}","name":"{name}","postcode":"{cp}","lat":"{lat}","lon":"{lon}","city":"{cityname}","departement":"{dept}","region":"{region}","importance":{importance},"housenumbers":{{{s_housenumbers}}}}}\n')
            for fantoir,citycode,type,name,postcode,lat,lon,city,departement,region,importance,housenumbers,*others in self.json_voies_rapprochees_data:
                s_housenumbers = ','.join([f'"{s.split("$")[0]}":{{"lat":{s.split("$")[1]},"lon":{s.split("$")[2]}}}' for s in housenumbers.split('#') ])
                jsonfile.write(f'{{"id":"{fantoir}","citycode":"{citycode}","type":"{type}","name":"{name}","postcode":"{cp}","lat":"{lat}","lon":"{lon}","city":"{cityname}","departement":"{dept}","region":"{region}","importance":{importance},"housenumbers":{{{s_housenumbers}}}}}\n')
               
    def move_to_web_directory(self):
        return True

def process(departements, **kwargs):
    for dept in departements:
        if not hp.is_valid_dept(dept):
            print(f"Code {dept} invalide pour un département - abandon")
            continue
        d = Dataset(dept)
        # d.save_as_shp()
        # d.save_as_csv()
        # d.save_as_ttl()
        d.save_as_json()
        d.move_to_web_directory()
