#!/bin/bash

set -e

$pgsql_CADASTRE -c "SELECT  source,etape, date_debut,date_fin,dept,cadastre_com,nom_com,nombre_adresses FROM batch ORDER BY id_batch DESC LIMIT 10;"
ps -eaf|grep 'bano'
ps -eaf|grep cumul
