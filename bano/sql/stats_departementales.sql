WITH previous 
AS 
(DELETE FROM  bano_stats_departementales RETURNING *)
INSERT INTO   bano_stats_departementales_cumul
SELECT        * 
FROM          previous;


INSERT INTO   bano_stats_departementales
WITH
nb_communes
AS
(SELECT dep, count(*) nb_communes
FROM    cog_commune
WHERE   typecom = 'COM'
GROUP BY dep),
nb_adresses_osm
AS
(SELECT dep, count(*) nb_adresses_osm
FROM    (SELECT code_insee AS com FROM bano_adresses WHERE source = 'OSM') o
JOIN    cog_commune
USING   (com)
GROUP BY 1),
nb_adresses_ban_par_rue
AS
(SELECT dep, code_insee, nom_voie, count(*) nb_adresses_ban_par_rue
FROM    cog_commune
JOIN    ban
ON      code_insee = com
GROUP BY 1,2,3),
nb_adresses_ban_par_dep
AS
(SELECT dep,
       sum(nb_adresses_ban_par_rue) as nb_adresses_ban_par_dep
FROM   nb_adresses_ban_par_rue
GROUP BY 1),
nb_voies_ban_par_dep
AS
(SELECT dep,
       count(*) as nb_voies_ban_par_dep
FROM   nb_adresses_ban_par_rue
GROUP BY 1),
nb_voies_ban_rapprochees
AS
(SELECT dep, count(*) AS nb_voies_ban_rapprochees
FROM (SELECT code_dept AS dep, fantoir FROM nom_fantoir WHERE source = 'OSM'
     INTERSECT
	 SELECT code_dept, fantoir FROM bano_adresses WHERE source = 'BAN')a
GROUP BY 1),
nb_bal
AS
(SELECT dep, count(*) AS nb_bal
FROM public.communes_summary
WHERE type_composition = 'bal'
GROUP BY 1),
nb_bal_100pct_certif
AS
(SELECT dep, count(*) AS nb_bal_100pct_certif
FROM public.communes_summary
WHERE nb_numeros = nb_numeros_certifies AND nb_numeros > 0
GROUP BY 1)
SELECT d.dep,
       nb_communes,
	COALESCE(nb_adresses_osm,0),
	nb_adresses_ban_par_dep,
	nb_voies_ban_par_dep,
	COALESCE(nb_voies_ban_rapprochees,0),
	COALESCE(nb_bal,0),
	COALESCE(nb_bal_100pct_certif,0)
FROM   cog_departement d
JOIN   nb_communes
USING (dep)
JOIN   nb_adresses_osm
USING (dep)
JOIN   nb_adresses_ban_par_dep
USING (dep)
JOIN   nb_voies_ban_par_dep
USING (dep)
JOIN   nb_voies_ban_rapprochees
USING (dep)
JOIN   nb_bal
USING (dep)
JOIN   nb_bal_100pct_certif
USING (dep);