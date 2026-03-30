INSERT INTO cog_commune(typecom,com,reg,dep,tncc,ncc,nccenr,libelle)
SELECT nature_zonage,
       com_comer,
       substr(com_comer,1,3), --reg
       substr(com_comer,1,3), --reg
       tncc,
       ncc,
       nccenr,
       libelle
FROM   cog_commune_comtom
LEFT JOIN (SELECT com FROM cog_commune) c
ON     (com_comer = com)
WHERE  com IS NULL;

INSERT INTO cog_departement(dep,reg,tncc,ncc,nccenr,libelle)
SELECT comer,
       comer,
       tncc,
          ncc,
          nccenr,
          libelle
FROM   cog_collectivite_comtom
LEFT OUTER JOIN (SELECT dep FROM cog_departement) AS d
ON dep = comer
WHERE dep IS NULL;

INSERT INTO cog_region(reg,tncc,ncc,nccenr,libelle)
SELECT comer,
       tncc,
          ncc,
          nccenr,
          libelle
FROM   cog_collectivite_comtom
LEFT OUTER JOIN (SELECT reg FROM cog_region) AS r
ON reg = comer
WHERE reg IS NULL;
