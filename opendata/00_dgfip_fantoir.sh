# nom du fichier dans le dossier 00_dgfip
FANTOIR=FANTOIR0116

# récupération et décompression du fichier FANTOIR
# wget http://www2.impots.gouv.fr/documentation/fantoir/fichier_national_fantoir.zip

cd 00_dgfip

# import dans SQL en format fixe (delimiter et quote spéciaux pour ignorer)
psql cadastre -c "create table if not exists dgfip_fantoir (raw text);"
psql cadastre -c "\copy dgfip_fantoir from '$FANTOIR' with csv delimiter '#' quote '>'"

psql cadastre -c "
truncate fantoir_voie_2015;
insert into fantoir_voie_2015 (select substr(raw,1,2) as code_dept, substr(raw,3,1) as code_dir, substr(raw,4,3) as code_com, substr(raw,1,2)||substr(raw,4,3) as code_insee, substr(raw,7,4) as id_voie, substr(raw,11,1) as cle_rivoli, rtrim(substr(raw,12,4)) as nature_voie, rtrim(substr(raw,16,26)) as libelle_voie,  substr(raw,49,1) as type_commune, substr(raw,50,1) as caractere_rur, substr(raw,51,1) as caractere_voie, substr(raw,52,1) as caractere_pop, substr(raw,60,7)::integer as pop_a_part, substr(raw,67,7)::integer as pop_fictive, substr(raw,74,1) as caractere_annul, substr(raw,75,7) as date_annul, substr(raw,82,7) as date_creation, substr(raw,104,5) as code_majic, substr(raw,109,1) as type_voie, substr(raw,110,1) as ld_bati, substr(raw,113,8) as dernier_mot from dgfip_fantoir where raw not like '______ %' and raw not like '___ %');
drop table dgfip_fantoir;
"


