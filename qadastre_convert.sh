#!/bin/bash

qadastre2OSM=/data/project/cadastre.openstreetmap.fr/bin/cadastre-housenumber/bano/Qadastre2OSM
bano_cache=/data/work/cadastre.openstreetmap.fr/bano_cache

echo  $bano_cache/$1/$2

cd $bano_cache/$1/$2
echo "$3"
$qadastre2OSM --convert $2 "$3"
