cd 059_lille
unzip -o lmcu_geocatalogue_1441747691.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre donnees/LM_SEUIL_point.shp  -overwrite -nlt GEOMETRY -nln import_lille


exit

psql cadastre -c "
delete from cumul_adresses where source='OD-Lille';
insert into cumul_adresses select wkb_geometry, trim(numero || ' ' || coalesce(complement,'')), right(auto_adres,-(length(numero::text)+length(coalesce(complement,''))+1)), null, rivoli_id::integer::text, comm_id::integer::text, null, '059',  cpostal, 'OD-Lille', null, null from import_lille;
"

# mise à jour des codes FANTOIR (manque la clé RIVOLI dans les données opendata)
psql cadastre -c "with f as (select od.fantoir, cle_rivoli from cumul_adresses od join fantoir_voie on (code_insee=insee_com and concat(code_insee,id_voie)=od.fantoir) where source = 'OD-Lille' group by a.fantoir, cle_rivoli) update cumul_adresses c set fantoir = concat(f.fantoir,f.cle_rivoli) from f where c.fantoir=f.fantoir and source = 'OD-Lille';"

# mise à jour du nom de voie depuis voie_osm dspo sur données OSM ou cadastre
psql cadastre -c "with v as (select od.fantoir, cu.voie_osm from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.voie_osm is not null and cu.voie_osm != '') where od.source = 'OD-Lille' and od.voie_osm is null group by od.fantoir, cu.voie_osm) update cumul_adresses c set voie_osm=v.voie_osm from v where c.voie_osm is null and c.fantoir=v.fantoir and c.source = 'OD-Lille';"

# mise à jour voie_osm depuis voie_cadastre sur libellés restants
psql cadastre -c "with v as (select od.fantoir, cu.voie_cadastre from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.source not like 'OD%') where od.source like 'OD-Lille' and od.voie_osm is null group by od.fantoir, cu.voie_cadastre order by od.fantoir) update cumul_adresses cu set voie_osm = v.voie_cadastre from v where cu.fantoir=v.fantoir and cu.source = 'OD-Lille';"

# mise à jour FANTOIR incorrect d'après libellés identiques Lille/FANTOIR
psql cadastre -c "with u as (select a.fantoir as rivoli_mel, f.fantoir||f.cle_rivoli as rivoli_fantoir from cumul_adresses a join fantoir_voie f on (code_insee like '59%' and code_insee=insee_com and voie_cadastre=nature_voie ||' '||libelle_voie and date_annul='0000000') where source='OD-Lille' and length(a.fantoir)<10 group by 1,2) update cumul_adresses set fantoir=rivoli_fantoir from u where fantoir=rivoli_mel and source='OD-Lille';"

# mise à jour FANTOIR incorrect d'après typevoie/nomvoie Lille/FANTOIR
psql cadastre -c "with u as (select a.fantoir as fantoir_mel, f.fantoir||f.cle_rivoli as fantoir_dgfip, voie_cadastre, nature_voie, libelle_voie from (select fantoir, voie_cadastre from cumul_adresses where source='OD-Lille' and length(fantoir)<10 group by 1,2) as a join (select rivoli_id::integer::text as rivoli_id, typevoie, nomvoie, comm_id::integer::text as insee from import_lille group by 1,2,3,4) as od on (a.fantoir=od.rivoli_id) join fantoir_voie f on (f.code_insee=od.insee and date_annul!='0000000' and nature_voie=typevoie and libelle_voie=nomvoie)) update cumul_adresses set fantoir=fantoir_dgfip from u where fantoir=fantoir_mel and source='OD-Lille';"

