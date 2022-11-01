UPDATE ban_odbl
SET nom_voie = TRANSLATE(nom_voie,'"','')
WHERE nom_voie LIKE '%"%';
COMMIT;