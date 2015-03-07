## http://opendata.regionpaca.fr/donnees/detail/base-de-donnees-adresses-de-laccm.html

cd /tmp
#wget 'http://opendata.regionpaca.fr/donnees.html?type=109&no_cache=1&tx_ausyopendata_pi1%5Bdataset%5D=283&tx_ausyopendata_pi1%5Bdatafile%5D=278&tx_ausyopendata_pi1%5Baction%5D=download&tx_ausyopendata_pi1%5Bcontroller%5D=Dataset&cHash=5d538731e8fa4c9f44d1a103dc452ab1' -O accm.zip
wget 'http://opendata.regionpaca.fr/donnees.html?type=109&no_cache=1&tx_ausyopendata_pi1%5Bdataset%5D=283&tx_ausyopendata_pi1%5Bdatafile%5D=278&tx_ausyopendata_pi1%5Baction%5D=download&tx_ausyopendata_pi1%5Bcontroller%5D=Dataset&cHash=5d538731e8fa4c9f44d1a103dc452ab1' -O accm.zip
unzip -o accm.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre ACCM-A-ADRESSES-2014/ADRESSE_ACCM.shp  -overwrite -nlt GEOMETRY -nln import_accm

psql cadastre -c "insert into cumul_adresses (select wkb_geometry, concat(num_voi,' ',suf_voi), concat(typevoie,' ',nomvoie), NULL, concat(codcomm,rivoli), codcomm, null, '013', code_posta, 'OD-ARLES', null from import_accm);"

# mise à jour des codes FANTOIR (manque la clé RIVOLI dans les données opendata)
psql cadastre -c "with f as (select fantoir, cle_rivoli from cumul_adresses join fantoir_voie on (code_insee=insee_com and concat(code_insee,id_voie)=fantoir) where source = 'OD-ARLES' group by fantoir, cle_rivoli) update cumul_adresses c set fantoir = concat(f.fantoir,f.cle_rivoli) from f where c.fantoir=f.fantoir and source like 'OD%';"

# mise à jour du nom de voie depuis voie_osm dspo sur données OSM ou cadastre
psql cadastre -c "with v as (select od.fantoir, cu.voie_osm from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.voie_osm is not null and cu.voie_osm != '') where od.source = 'OD-ARLES' and od.voie_osm is null group by od.fantoir, cu.voie_osm) update cumul_adresses c set voie_osm=v.voie_osm from v where c.voie_osm is null and c.fantoir=v.fantoir and c.source = 'OD-ARLES';"

# mise à jour voie_osm depuis voie_cadastre sur libellés restants
psql cadastre -c "with v as (select od.fantoir, cu.voie_cadastre from cumul_adresses od join cumul_adresses cu on (cu.fantoir=od.fantoir and cu.source not like 'OD%') where od.source like 'OD-ARLES' and od.voie_osm is null group by od.fantoir, cu.voie_cadastre order by od.fantoir) update cumul_adresses cu set voie_osm = v.voie_cadastre from v where cu.fantoir=v.fantoir and cu.source like 'OD%';"

