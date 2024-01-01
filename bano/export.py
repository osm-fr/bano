#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import os
import sys
import subprocess

from pathlib import Path

from .sql import sql_get_data,sql_get_dict_data,sql_process
from . import constants
from . import helpers as hp

class Dataset:
    def __init__(self, dept):
        self.dept = dept
        self.csv_data = None
        self.json_commune_data = None
        self.json_voies_rapprochees_data = None
        self.json_voies_rapprochees_sans_adresses_data = None
        self.json_voies_non_rapprochees_data = None
        self.json_lieux_dits_data = None

    def get_csv_data(self):
        self.csv_data = sql_get_data('export_csv_dept',dict(dept=self.dept))

    def get_json_commune_data(self):
        self.json_commune_data = sql_get_dict_data('export_json_dept_communes',dict(dept=self.dept))
        # print(json.dumps(self.json_commune_data))

    # def get_json_voies_non_rapprochees_data(self):
    #     return sql_get_data('export_json_dept_voies_non_rapprochees',dict(dept=self.dept))

    # def get_json_voies_rapprochees_data(self):
    #     return sql_get_data('export_json_dept_voies_rapprochees',dict(dept=self.dept))

    def get_json_voies_avec_adresses_data(self):
        self.json_voies_avec_adresses_data = sql_get_dict_data('export_json_dept_voies_avec_adresses',dict(dept=self.dept))
        # for j in self.json_voies_avec_adresses_data:
        #     j['housenumbers'] = [{p.split('$')[0]:{'lat':p.split('$')[1],'lon':p.split('$')[2]}} for p in j['housenumbers'].split('@')]
        #     jl = json.dumps(j)
        #     print(jl)
        # print(json.dumps(self.json_voies_avec_adresses_data))

    def get_json_lieux_dits_data(self):
        return sql_get_data('export_json_dept_lieux_dits',dict(dept=self.dept))

    def get_target_filename(self,filetype):
        return f'bano-{self.dept}.{filetype}'

    def get_sas_full_filename(self,filetype):
        return Path(os.environ['EXPORT_SAS_DIR']) / self.get_target_filename(filetype)

    def get_webdir_full_filename(self,filetype):
        return Path(os.environ['EXPORT_WEB_DIR']) / self.get_target_filename(filetype)

    def save_as_csv(self):
        if not self.csv_data :
            self.csv_data = self.get_csv_data()
        with open(self.get_sas_full_filename('csv'),'w', newline='') as csvfile:
            writer = csv.writer(csvfile,dialect='unix',quoting=csv.QUOTE_MINIMAL)
            writer.writerows([l[0:-1] for l in self.csv_data])

    def save_as_ttl(self):
        if not self.csv_data :
            self.csv_data = self.get_csv_data()
        with open(self.get_sas_full_filename('ttl'),'w') as ttlfile:
            ttlfile.write(f"""@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix locn: <http://www.w3.org/ns/locn#> .
@prefix gn: <http://www.geonames.org/ontology#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix gsp: <http://www.opengis.net/ont/geosparql#> .
@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://www.openstreetmap.fr/bano/data/> a dcat:Catalog ;
\tdcterms:title "Donnees des adresses du projet BANO (Base Adresse Nationale Ouverte) en RDF"@fr ;
\tdcterms:description "Le projet BANO en RDF de Base d\'Adresses Nationale Ouverte initie par OpenStreetMap France."@fr ;
\tfoaf:homepage <http://openstreetmap.fr/bano> ;
\tdcterms:language "fr" ;
\tdcterms:license <http://www.opendatacommons.org/licenses/odbl/> ;
\tdcterms:publisher <http://www.openstreetmap.fr/> ; #url openstreetmap France
\tdcterms:issued "2014-05-14"^^xsd:date ; # data issued
\tdcterms:modified "2014-08-21"^^xsd:date ; #last modification
\tdcterms:spatial <http://id.insee.fr/geo/departement/{self.dept}>, <http://id.insee.fr/geo/pays/france> ; # region/pays (France)
\t.
""")
            for id,numero,voie,cp,ville,source,lat,lon,*others in self.csv_data:
                ttlfile.write(f"""<http://id.osmfr.org/bano/{id}>  a locn:Address , gn:Feature ;
locn:fullAddress "{numero} {voie}, {cp} {ville}, FRANCE";
locn:addressId "{id}" ;
locn:locatorDesignator "{numero}" ;
locn:thoroughfare "{voie}"@fr ;
locn:postalCode "{cp}" ;
locn:locatorName "{ville}"@fr ;
locn:adminUnitL1 "FR" ;""")
# traitement des arrondissements municipaux de Paris, Lyon, Marseille
                if id[0:2] in '13 69 75' and (int(id[0:5]) in range(13201, 13217) or int(id[0:5]) in range(69381, 69370) or int(id[0:5]) in range(75101, 75121)):
                    ttlfile.write(f"locn:location <http://id.insee.fr/geo/arrondissementMunicipal/{id[0:5]}> ;")
                else:
                    ttlfile.write(f"locn:location <http://id.insee.fr/geo/commune/{id}[0:5]> ;")
                ttlfile.write(f"""locn:geometry <geo:{lat},{lon};u=0;crs=wgs84> ;
locn:geometry [a geo:Point ; geo:lat "{lat}" ; geo:long "{lon}" ] ;
locn:geometry [a gsp:Geometry; gsp:asWKT "POINT({lon} {lat})"^^gsp:wktLiteral ] ;
.""")


    def save_as_shp(self):
        subprocess.run(['ogr2ogr', '-f',"ESRI Shapefile", '-lco', 'ENCODING=UTF-8', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:4326', '-overwrite', self.get_sas_full_filename('shp'), 'PG:dbname=cadastre user=cadastre', '-sql', f'{self.csv_query}'])

    def save_as_json(self):
        with open(self.get_sas_full_filename('json'),'w') as jsonfile:
            for l in self.json_commune_data:
                jsonfile.write(f"{json.dumps(l,ensure_ascii=False,separators=(',',':'))}\n")
            for l in self.json_voies_avec_adresses_data:
                dict_hsnr = {}
                for p in l['housenumbers'].split('@'):
                    numero,lat,lon = p.split('$')
                    dict_hsnr[numero] = dict(lat=float(lat),lon=float(lon))
                l['housenumbers'] = dict_hsnr
                jsonfile.write(f"{json.dumps(l,ensure_ascii=False,separators=(',',':'))}\n")

            # for fantoir,citycode,type,name,postcode,lat,lon,cityname,departement,region,importance in self.json_voies_rapprochees_sans_adresses_data:
            #         if ';' in postcode:
            #             postcode = postcode.split(';')
            #         jsonfile.write(f'{{"id":"{fantoir}","citycode":"{citycode}","type":"{type}","name":"{name}","postcode":{json.dumps(postcode)},"lat":"{lat}","lon":"{lon}","city":"{cityname}","departement":"{departement}","region":"{region}","importance":{importance}}}\n')
            # if not self.json_lieux_dits_data :
            #     self.json_lieux_dits_data = self.get_json_lieux_dits_data()
            # for fantoir,citycode,type,name,postcode,lat,lon,cityname,departement,region,importance,*others in self.json_lieux_dits_data:
            #         if ';' in postcode:
            #             postcode = postcode.split(';')
            #         jsonfile.write(f'{{"id":"{fantoir}","citycode":"{citycode}","type":"{type}","name":"{name}","postcode":{json.dumps(postcode)},"lat":"{lat}","lon":"{lon}","city":"{cityname}","departement":"{departement}","region":"{region}","importance":{importance}}}\n')
               
def process(departements, **kwargs):
    sql_process('table_polygones_postaux',dict())
    sql_process('tables_export',dict())
    for dept in departements:
        if not hp.is_valid_dept(dept):
            print(f"Code {dept} invalide pour un département - abandon")
            continue
        d = Dataset(dept)
        # d.save_as_shp()
        # d.save_as_csv()
        # d.save_as_ttl()
        d.get_json_commune_data()
        d.get_json_voies_avec_adresses_data()
        d.save_as_json()
