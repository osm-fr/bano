psql cadastre -c "drop table import_sete;"
psql cadastre -c "create table import_sete (id integer, lon numeric, lat numeric, numero text, lib_abbreg text, lib_complet text, fantoir text, cle_rivoli text, commune text, insee_com text, code_postal text, lieu_dit text);"
psql cadastre -c "\copy import_sete from '/home/cquest/Bano34301.csv' with (format csv, header true, delimiter ';');"

psql cadastre -c "delete from cumul_adresses where source = 'OD-SETE';"
psql cadastre -c "insert into cumul_adresses select st_setsrid(st_point(lon,lat),4326),numero, null, lib_complet, insee_com || fantoir ||cle_rivoli, insee_com, null, '034',code_postal,'OD-SETE',null,lib_abbreg from import_sete;"

