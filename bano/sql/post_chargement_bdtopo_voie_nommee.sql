CREATE TEMP TABLE nom_collaboratif_type_voie
AS
WITH
vals (abbrev,dvp)
AS
(VALUES('ACH','Ancien Chemin'),
       ('ALL','Allée'),
       ('AV','Avenue'),
       ('BD','Boulevard'),
       ('CAL','Calade'),
       ('CALL','Calade'),
       ('CHE','Chemin'),
       ('CRS','Cours'),
       ('DOM','Domaine'),
       ('ESC','Escalier'),
       ('ESP','Esplanade'),
       ('FRM','Ferme'),
       ('HAM','Hameau'),
       ('IMP','Impasse'),
       ('LOT','Lotissement'),
       ('MLN','Moulin'),
       ('MTE','Montée'),
       ('PAS','Passage'),
       ('PASS','Passage'),
       ('PCH','Petit Chemin'),
       ('PKG','Parking'),
       ('PL','Place'),
       ('PRV','Parvis'),
       ('PROM','Promenade'),
       ('PTR','Petite Route'),
       ('R','Rue'),
       ('Q','Quai'),
       ('QU','Quai'),
       ('QUA','Quartier'),
       ('RES','Résidence'),
       ('RLE','Ruelle'),
       ('RPT','Rond-point'),
       ('RTE','Route'),
       ('SEN','Sentier'),
       ('SQ','Square'),
       ('TRA','Traverse'),
       ('VEN','Venelle'),
       ('VGE','Village'),
       ('VLA','Villa'),
       ('VOI','Voie')
       ),
p
AS
(SELECT *,
        POSITION(' ' IN nom_collaboratif) AS pos,
        UPPER(SUBSTRING(nom_collaboratif FROM 1 FOR POSITION(' ' IN nom_collaboratif)-1)) AS abbrev
FROM    bdtopo_voie_nommee
WHERE   COALESCE(identifiant_voie_ban,'') = '' AND
        nom_collaboratif LIKE '% %')
SELECT  DISTINCT nom_collaboratif,
        dvp||' '||SUBSTR(nom_collaboratif, pos+1) AS nom_collaboratif_dvp
FROM    p
JOIN    vals
USING   (abbrev);

DROP TABLE IF EXISTS bdtopo_voie_nommee_utile CASCADE;
CREATE TABLE bdtopo_voie_nommee_utile
AS
SELECT insee_commune AS code_insee,
       COALESCE(nom_collaboratif_dvp,nom_collaboratif) AS nom_collaboratif,
       COALESCE(identifiant_voie_ban,'') = '' AS utile,
       geometrie
FROM   bdtopo_voie_nommee
LEFT OUTER JOIN nom_collaboratif_type_voie
USING (nom_collaboratif)
WHERE COALESCE(TRIM(BOTH FROM nom_collaboratif),'') != '';

CREATE INDEX idx_bdtopo_voie_nommee_utile_code_insee ON bdtopo_voie_nommee_utile (code_insee);