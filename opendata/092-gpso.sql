DELETE FROM cumul_adresses WHERE source = 'OD-GPSO';
WITH
a AS (	SELECT 	replace(replace(type_voie||' '||coalesce(prefixe_vo,'')||' '||nom_voie,''' ',''''),'  ',' ') voie_cadastre,
		trim(numero||' '||coalesce(numero_ext,'')) numero_complet,
		*
	FROM 	import_gpso_cadastre),
b AS (	SELECT 	DISTINCT code_rivol,nom_voie FROM import_gpso_cadastre),
c AS (	SELECT 	code_rivol FROM b GROUP BY 1 HAVING count(*) > 1),
d AS (	SELECT 	a.*,c.code_rivol bad_code FROM a LEFT OUTER JOIN c ON a.code_rivol = c.code_rivol),
e AS (	SELECT 	f.code_insee||f.id_voie||f.cle_rivoli fantoir,
		CASE 
			WHEN bad_code IS NULL THEN c.voie_osm
			ELSE ' '
		END voie_osm,
		d.*
	FROM d
	LEFT OUTER JOIN fantoir_voie f
	ON d.code_rivol = f.code_insee||'_'||f.id_voie
	LEFT OUTER JOIN cumul_voies c
	ON f.code_insee||f.id_voie||f.cle_rivoli = c.fantoir)
INSERT INTO cumul_adresses
SELECT 	DISTINCT wkb_geometry,
	numero_complet,
	voie_cadastre,
	voie_osm,
	fantoir,
	code_insee,
	NULL,
	'092'::text,
	code_posta,
	'OD-GPSO'::text,
	NULL::integer,
	NULL
FROM	e;
