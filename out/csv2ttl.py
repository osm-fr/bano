import sys
import csv
import string

print('@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .')
print('@prefix locn: <http://www.w3.org/ns/locn#> .')
print('@prefix gn: <http://www.geonames.org/ontology#> .')
print('@prefix prov: <http://www.w3.org/ns/prov#> .')
print('@prefix gsp: <http://www.opengis.net/ont/geosparql#> .')
print('@prefix geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> .')
print('@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .')
print('@prefix dcat: <http://www.w3.org/ns/dcat#> .')
print('@prefix foaf: <http://xmlns.com/foaf/0.1/> .')
print('@prefix dcterms: <http://purl.org/dc/terms/> .')
print
print('<http://www.openstreetmap.fr/bano/data/> a dcat:Catalog ;')
print('		dcterms:title "Donnees des adresses du projet BANO (Base Adresse Nationale Ouverte) en RDF"@fr ;')
print('		dcterms:description "Le projet BANO en RDF de Base d\'Adresses Nationale Ouverte initie par OpenStreetMap France."@fr ;')
print('		foaf:homepage <http://openstreetmap.fr/bano> ;')
print('		dcterms:language "fr" ;')
print('		dcterms:license <http://www.opendatacommons.org/licenses/odbl/> ;')
print('		dcterms:publisher <http://www.openstreetmap.fr/> ; #url openstreetmap France')
print('		dcterms:issued "2014-05-14"^^xsd:date ; # data issued')
print('		dcterms:modified "2014-08-21"^^xsd:date ; #last modification')
print('		dcterms:spatial <http://id.insee.fr/geo/departement/'+sys.argv[2]+'>, <http://id.insee.fr/geo/pays/france> ; # region/pays (France)')
print('		.')
print
with open(sys.argv[1]) as csvfile:
	addr = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in addr:
		print('<http://id.osmfr.org/bano/'+row[0]+'>  a locn:Address , gn:Feature ;')
		print('	locn:fullAddress "'+row[1]+' '+row[2]+', '+row[3]+' '+row[4]+', FRANCE";');
		print('	locn:addressId "'+row[0]+'" ;')
		print('	locn:locatorDesignator "'+row[1]+'" ;')
		print('	locn:thoroughfare "'+row[2]+'"@fr ;')
		print('	locn:postalCode "'+row[3]+'" ;')
		print('	locn:locatorName "'+row[4]+'"@fr ;')
		print('	locn:adminUnitL1 "FR" ;')
		# traitement des arrondissements municipaux de Paris, Lyon, Marseille
		if (sys.argv[2] in ['13','69','75'] and int(row[0][0:5])) in range(13201, 13217)+range(69381, 69370)+range(75101, 75121):
			print('	locn:location <http://id.insee.fr/geo/arrondissementMunicipal/'+row[0][0:5]+'> ;')
		else:
			print('	locn:location <http://id.insee.fr/geo/commune/'+row[0][0:5]+'> ;')
		print('	locn:geometry <geo:'+row[6]+','+row[7]+';u=0;crs=wgs84> ;')
		print('	locn:geometry [a geo:Point ; geo:lat "'+row[6]+'" ; geo:long "'+row[7]+'" ] ;')
		print('	locn:geometry [a gsp:Geometry; gsp:asWKT "POINT('+row[7]+' '+row[6]+')"^^gsp:wktLiteral ] ;')
		print('	.')
		print
