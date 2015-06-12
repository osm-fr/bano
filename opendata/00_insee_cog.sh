cd 00_insee
wget -nc http://www.insee.fr/fr/methodes/nomenclatures/cog/telechargement/2014/txt/comsimp2014.zip
unzip -o comsimp2014.zip
iconv comsimp2014.txt -f ISO8859-1 -t UTF8 > comsimp2014.csv
psql cadastre -c "drop table cog2014; create table cog2014 (cdc integer, cheflieu integer, reg text, dep text, com text, ar text, ct text, tncc text, artmaj text, ncc text, artmin text, nccenr text);"
psql cadastre -c "truncate table cog2014;"
psql cadastre -c "\copy cog2014 from '/tmp/comsimp2014.csv' with (format csv, delimiter E'\t', header true);"
psql cadastre -c "alter table cog2014 add column insee_com text;"
psql cadastre -c "update cog2014 set insee_com=dep||com;"
psql cadastre -c "create index on cog2014 (insee_com);"

