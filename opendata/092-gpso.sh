cd 092-gpso

rm -rf unzip GPSO_MIG92_Base_PT_Adresse.*
wget https://www.data.gouv.fr/s/resources/point-adresse-2/20150605-114705/GPSO_MIG92_Base_PT_Adresse.zip
unzip GPSO_MIG92_Base_PT_Adresse.zip

ogr2ogr -s_srs EPSG:3949 -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre GPSO_MIG92_Base_PT_Adresse.shp -overwrite -nlt GEOMETRY -nln import_gpso_cadastre
cd -
psql -d cadastre -f 092-gpso.sql

#psql cadastre -c "
#delete from cumul_adresses where source='OD-GPSO';
#insert into cumul_adresses select st_transform(st_setsrid(st_point(x_rgf93cc4, y_rgf93cc4),3949),4326), trim(numero||' '||coalesce(numero_ext,'')) as numero, replace(replace(trim(format('%s %s %s',i.type_voie, prefixe_vo, nom_voie)),'  ',' '),chr(39)||' ',chr(39)) as voie_cadastre, '', replace(code_rivol,'_','')||coalesce(cle_rivoli,''), i.code_insee, null, '092', code_posta, 'OD-GPSO',null,null from import_gpso i join fantoir_voie f on (i.code_insee=f.code_insee and id_voie=substr(code_rivol,7,4));
#"