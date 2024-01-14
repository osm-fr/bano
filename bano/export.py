#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import os
import sys
import subprocess

from pathlib import Path

from .sql import sql_get_data,sql_get_dict_data,sql_process,sql_query
from . import constants
from . import helpers as hp

def get_csv_data(dept):
    return sql_get_data('export_csv_dept',dict(dept=dept))

def save_as_csv(dept,csv_data):
    with open(get_sas_full_filename(dept,'csv'),'w', newline='') as csvfile:
        writer = csv.writer(csvfile,dialect='unix',quoting=csv.QUOTE_MINIMAL)
        writer.writerows([l[0:-1] for l in csv_data])

def save_as_ttl(dept,csv_data):
    with open(get_sas_full_filename(dept,'ttl'),'w') as ttlfile:
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
\tdcterms:spatial <http://id.insee.fr/geo/departement/{dept}>, <http://id.insee.fr/geo/pays/france> ; # region/pays (France)
\t.
""")
        for id,numero,voie,cp,ville,source,lat,lon,*others in csv_data:
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


def save_as_shp(dept):
    # query = sql_query('export_csv_dept',dict(dept=dept))
    subprocess.run(['ogr2ogr', '-f',"ESRI Shapefile", '-lco', 'ENCODING=UTF-8', '-s_srs', 'EPSG:4326', '-t_srs', 'EPSG:4326', '-overwrite', get_sas_full_filename(dept,'shp'), 'PG:dbname=bano user=cadastre', '-sql', sql_query('export_csv_dept',dict(dept=dept))])

def save_as_json(dept):
    with open(get_sas_full_filename(dept,'json'),'w') as jsonfile:
        for l in sql_get_dict_data('export_json_dept_communes',dict(dept=dept)):
            if ';' in l['postcode']:
                l['postcode'] = l['postcode'].split(';')
                print(l['postcode'])
            jsonfile.write(f"{json.dumps(l,ensure_ascii=False,separators=(',',':'))}\n")
        for l in sql_get_dict_data('export_json_dept_voies_avec_adresses',dict(dept=dept)):
            dict_hsnr = {}
            for p in l['housenumbers'].split('@'):
                numero,lat,lon = p.split('$')
                dict_hsnr[numero] = dict(lat=float(lat),lon=float(lon))
            l['housenumbers'] = dict_hsnr
            jsonfile.write(f"{json.dumps(l,ensure_ascii=False,separators=(',',':'))}\n")
        for l in sql_get_dict_data('export_json_dept_voies_ld_sans_adresses',dict(dept=dept)):
            jsonfile.write(f"{json.dumps(l,ensure_ascii=False,separators=(',',':'))}\n")

def get_target_filename(dept,filetype):
    return f'bano-{dept}.{filetype}'

def get_sas_full_filename(dept,filetype):
    return Path(os.environ['EXPORT_SAS_DIR']) / get_target_filename(dept,filetype)

def get_webdir_full_filename(dept,filetype):
    return Path(os.environ['EXPORT_WEB_DIR']) / get_target_filename(dept,filetype)

def prepare_export(**kwargs):
    sql_process('table_polygones_postaux',dict())
    sql_process('tables_export',dict())

def process(departements, **kwargs):
    for dept in departements:
        if not hp.is_valid_dept(dept):
            print(f"Code {dept} invalide pour un département - abandon")
            continue
        save_as_shp(dept)
        csv_data = get_csv_data(dept)
        save_as_csv(dept,csv_data)
        save_as_ttl(dept,csv_data)
        # save_as_json(dept)
