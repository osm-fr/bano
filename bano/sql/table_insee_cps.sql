DROP TABLE IF EXISTS insee_codes_postaux CASCADE;
CREATE UNLOGGED TABLE insee_codes_postaux
AS
SELECT insee AS code_insee,
       STRING_AGG(cp,';')
FROM   (SELECT DISTINCT insee, cp FROM codes_postaux ORDER BY 1,2) AS c
GROUP BY 1;