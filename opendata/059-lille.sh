cd 059_lille
unzip -o lmcu_geocatalogue_1441747691.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre donnees/LM_SEUIL_point.shp  -overwrite -nlt GEOMETRY -nln import_lille


exit

psql cadastre -c "
delete from cumul_adresses where source='OD-Lille';
insert into cumul_adresses select wkb_geometry, numero || ' ' || complement, typevoie || ' ' || nomvoie, null, rivoli_id, comm_id, null, '059',  cpostal, 'OD-Lille', null, null from import_lille;
"

# mise à jour des codes FANTOIR (manque la clé RIVOLI dans les données opendata)
psql cadastre -c "with f as (select a.fantoir, cle_rivoli from cumul_adresses join fantoir_voie on (code_insee=insee_com and concat(code_insee,id_voie)=a.fantoir) where source = 'OD-Lille' group by a.fantoir, cle_rivoli) update cumul_adresses c set fantoir = concat(f.fantoir,f.cle_rivoli) from f where c.fantoir=f.fantoir and source = 'OD-Lille';"

# mise à jour du nom de voie depuis voie_osm dspo sur données OSM ou cadastre
psql cadastre -c "with v as (select od.fantoir, cu.voie_osm from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.voie_osm is not null and cu.voie_osm != '') where od.source = 'OD-Lille' and od.voie_osm is null group by od.fantoir, cu.voie_osm) update cumul_adresses c set voie_osm=v.voie_osm from v where c.voie_osm is null and c.fantoir=v.fantoir and c.source = 'OD-Lille';"

# mise à jour voie_osm depuis voie_cadastre sur libellés restants
psql cadastre -c "with v as (select od.fantoir, cu.voie_cadastre from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.source not like 'OD%') where od.source like 'OD-Lille' and od.voie_osm is null group by od.fantoir, cu.voie_cadastre order by od.fantoir) update cumul_adresses cu set voie_osm = v.voie_cadastre from v where cu.fantoir=v.fantoir and cu.source = 'OD-Lille';"

