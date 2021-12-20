SELECT :'dept'||'%' AS deptlike 
\gset
DELETE FROM :schema_cible.batiments WHERE insee_com LIKE :'deptlike';
INSERT INTO :schema_cible.batiments (insee_com,
                       nom,
                       type_batiment,
                       created,
                       updated,
                       geometrie)
SELECT commune,
       nom,
       "type",
       created,
       updated,
       geometrie
FROM   tmp_batiments:dept;
DROP TABLE tmp_batiments:dept;