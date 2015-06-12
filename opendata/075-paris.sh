cd 075_paris

# récupération des shapefile contenant les points adresse
curl 'http://opendata.paris.fr/explore/dataset/adresse_paris/download/?format=csv' > paris.csv

psql cadastre -c "drop table if exists import_paris; create table import_paris (geom_x_y text,geom text,n_sq_ad text,n_voie text,c_suf1 text,c_suf2 text,c_suf3 text,c_ar text,a_nvoie text,b_angle text,b_offstdf text,b_affstdf text,b_hors75 text,l_nvoie text,l_adr text,n_sq_ar text,n_sq_vo text,objectid text);"
psql cadastre -c "\copy import_paris from paris.csv with (format csv, header true, delimiter ';');"

# création des adresses dans cumul_adresses SANS données FANTOIR
psql cadastre -c "
begin;
delete from cumul_adresses where source='OD-PARIS';
insert into cumul_adresses select st_setsrid(st_point(substring(geom_x_y,position(',' in geom_x_y)+1)::numeric,left(geom_x_y,position(',' in geom_x_y)-1)::numeric),4326), trim(n_voie ||' '|| replace(replace(replace(replace(lower(c_suf1),'b','bis'),'t','ter'),'q','quater'),'c','quinquies')) as numero, substring(l_adr,length(l_nvoie)+2) as voie_cadastre, null as voie_nom, null as fantoir, '751'||right('0'||c_ar,2) as insee_com, null as cadastre_com,'075' as dept, null as code_postal, 'OD-PARIS' as source, null as batch_import_id, null as voie_fantoir from import_paris;
-- remise en forme bis/ter/quater/quinquies
update cumul_adresses set numero= trim(replace(numero,'b',' bis ')) where source='OD-PARIS' and numero ~ 'b';
update cumul_adresses set numero= trim(replace(numero,'t',' ter ')) where source='OD-PARIS' and numero ~ 't';
update cumul_adresses set numero= trim(replace(numero,'q',' quater ')) where source='OD-PARIS' and numero ~ 'q';
update cumul_adresses set numero= trim(replace(numero,'c',' quinquies ')) where source='OD-PARIS' and numero ~ 'c';
commit;
"

# mise à jour des codes FANTOIR et noms de voie
psql cadastre -c "
-- mise à jour des codes FANTOIR
-- noms identiques
with u as (select r.insee_com as u_insee, r.voie_cadastre as u_voie, f.id_voie, f.cle_rivoli from (select insee_com, voie_cadastre from cumul_adresses where source='OD-PARIS' group by 1,2) as r left join fantoir_voie f on (f.code_insee like '75%' and f.code_insee=r.insee_com and r.voie_cadastre = trim(f.nature_voie ||' '||f.libelle_voie))) update cumul_adresses set fantoir=u_insee||id_voie||cle_rivoli from u where source='OD-PARIS' and insee_com=u_insee and voie_cadastre=u_voie;

-- désabréviations
update cumul_adresses set voie_cadastre = regexp_replace(voie_cadastre,'^PRT ','PORT ') where voie_cadastre like 'PRT %' and source='OD-PARIS';
update cumul_adresses set voie_cadastre = regexp_replace(voie_cadastre,'^PER ','PERISTYLE ') where voie_cadastre like 'PER %' and source='OD-PARIS';
update cumul_adresses set voie_cadastre = regexp_replace(voie_cadastre,'^QU ','QUAI ') where voie_cadastre like 'QU %' and source='OD-PARIS';
update cumul_adresses set voie_cadastre = regexp_replace(voie_cadastre,' SAINT-',' ST ') where voie_cadastre like '% SAINT-%' and source='OD-PARIS';
update cumul_adresses set voie_cadastre = regexp_replace(voie_cadastre,' NOTRE-DAME ',' N D ') where voie_cadastre like '% NOTRE-DAME %' and source='OD-PARIS';

-- rapprochement
with u as (select r.insee_com as u_insee, r.voie_cadastre as u_voie, f.id_voie, f.cle_rivoli from (select insee_com, voie_cadastre from cumul_adresses where source='OD-PARIS' and fantoir is null group by 1,2) as r join fantoir_voie f on (f.code_insee like '75%' and f.code_insee=r.insee_com and replace(replace(replace(r.voie_cadastre,chr(39),' '),'-',' '),'  ',' ') = trim(f.nature_voie ||' '||f.libelle_voie))) update cumul_adresses set fantoir=u_insee||id_voie||cle_rivoli from u where source='OD-PARIS' and insee_com=u_insee and voie_cadastre=u_voie;

-- mise à jour à partir de la liste manuelle (dans import_paris_fantoir)
with u as(select insee as u_insee,nom as u_nom,right('0000'||fantoir,4) as u_fantoir from import_paris_fantoir where noms !='' and fantoir !='' and not fantoir like '%,%') update cumul_adresses set fantoir=u_insee||u_fantoir from u where source='OD-PARIS' and fantoir is null and insee_com=u_insee and voie_cadastre=u_nom;

-- ajout cle rivoli
with u as (select fantoir as u_fantoir, cle_rivoli as u_cle from cumul_adresses join fantoir_voie on (code_insee like '75%' and code_insee||id_voie=fantoir) where source='OD-PARIS' and length(fantoir)=9 group by 1,2) update cumul_adresses set fantoir=u_fantoir||u_cle from u where source='OD-PARIS' and fantoir=u_fantoir ;

-- ajout voie_osm à partir de cumul_voies
with u as (select a.fantoir as u_fantoir, v.voie_osm as u_nom from cumul_adresses a join cumul_voies v on (v.fantoir=a.fantoir) where a.source='OD-PARIS' and a.voie_osm is null and v.voie_osm != '' group by 1,2) update cumul_adresses set voie_osm=u_nom from u where source='OD-PARIS' and voie_osm is null and fantoir=u_fantoir;
"
