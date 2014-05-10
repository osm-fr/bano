#!/bin/bash

. config || exit -1

if [[ $# != 3 && $# != 4 ]] ; then
    echo "ERREUR: mauvais nombre d'arguments"
    exit -1
fi
code_departement=$1
code_commune=$2
nom_commune=$3
bis=$4

if [ ${#code_departement} != 3 ] ; then
    echo "ERREUR: le code département doit avoir 3 caractères"
    exit -1
fi
if [ ${#code_commune} != 5 ] ; then
    echo "ERREUR: le code commune doit avoir 5 caractères"
    exit -1
fi

#
# Déduit le code INSEE
#
if [ ${code_departement:0:1} == "0" ] ; then
    code_insee=${code_departement:1:2}${code_commune:2:3}
else
  if [ ${code_departement:2:1} != ${code_commune:2:1} ] ; then
    echo "ERREUR: le code commune ne correspond pas au code departement"
    exit -1
  fi
  code_insee=${code_departement:0:2}${code_commune:2:3}
fi


#
# Lance la génération des adresses:
#

depdir="$data_dir/$code_departement"
communedir="$hidden_dir/$code_departement/$code_commune"
if [ "$bis" = "false" ] ; then
  nobis="-nobis"
fi

command1="env LD_LIBRARY_PATH=/home/tyndare/.local/lib/ PYTHONPATH=/home/tyndare/.local/lib/python2.7/site-packages/ $PWD/cadastre_vers_osm_adresses_pour_bano.py $nobis $code_departement $code_commune"
command1dir="$communedir"

# command2="python addr_fantoir_building.py $code_insee $code_commune"
# command2dir=$PWD/cadastre-housenumber/associatedStreet

# command3="$PWD/cadastre-housenumber/supprime_relations_associatedStreet.py"

# file1="${depdir}/${code_commune}-${nom_commune}-adresses-associatedStreet_sans_batiment.zip"
# file2="${depdir}/${code_commune}-${nom_commune}-adresses-associatedStreet_mix_en_facade_ou_isole.zip"
# file3="${depdir}/${code_commune}-${nom_commune}-adresses-associatedStreet_tag_sur_batiment.zip"
# file4="${depdir}/${code_commune}-${nom_commune}-adresses-associatedStreet_point_sur_batiment.zip"

mkdir -p $communedir
chmod 02775 $communedir

cd $command1dir && $command1 || exit -1
# mv "$communedir/${code_commune}-adresses.zip" "${file1}"
# mv "$communedir/${code_commune}-adresses_buildings_proches.zip" "${file2}"
# $command3 "${file1}" "${file1/associatedStreet/addrstreet}"
# $command3 "${file2}" "${file2/associatedStreet/addrstreet}"

# cd $command2dir && $command2 || exit -1

# mv "$communedir/${code_commune}_adresse_tag_sur_batiment.zip" "${file3}"
# mv "$communedir/${code_commune}_adresse_point_sur_batiment.zip" "${file4}"
# $command3 "${file3}" "${file3/associatedStreet/addrstreet}"
# $command3 "${file4}" "${file4/associatedStreet/addrstreet}"


