# récupération et décompression du fichier FANTOIR
wget https://www.data.gouv.fr/s/resources/base-officielle-des-codes-postaux/20141106-120608/code_postaux_v201410.csv
iconv -f iso8859-1 -t utf8 code_postaux_v201410.csv > code_postaux_v201410-utf.csv
# import dans SQL en format fixe (delimiter et quote spéciaux pour ignorer)
psql cadastre -c "create table if not exists laposte_cp (insee text, commune text, cp text, libelle text); truncate table laposte_cp;"
psql cadastre -c "\copy laposte_cp from 'code_postaux_v201410-utf.csv' with (format csv, delimiter ';', quote '>', header true);"
psql cadastre -c "UPDATE laposte_cp SET commune=trim(commune), libelle=trim(libelle);"

# ajout de BIHOREL (manquant dans fichier La Poste)
psql cadastre -c "insert into laposte_cp values ('76095','BIHOREL','76420','BIHOREL');"

