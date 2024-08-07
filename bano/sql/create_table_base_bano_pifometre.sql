CREATE TABLE IF NOT EXISTS statut_fantoir (
	fantoir character varying(10),
	id_statut integer,
	timestamp_statut double precision,
	code_insee character(5));

CREATE INDEX IF NOT EXISTS idx_statut_fantoir_insee ON statut_fantoir(code_insee);
CREATE INDEX IF NOT EXISTS idx_statut_fantoir_fantoir ON statut_fantoir(fantoir);

CREATE TABLE IF NOT EXISTS labels_statuts_fantoir(
	id_statut integer primary key,
	tri integer default 0,
	label_statut character varying(200)
);
TRUNCATE labels_statuts_fantoir;
INSERT INTO labels_statuts_fantoir (id_statut,tri,label_statut)
VALUES (0,0,'Ok'),
(1,1,'Erreur d''orthographe'),
(2,2,'Divergence d''orthographe'),
(3,3,'Nom différent'),
(4,4,'Type de voie différent'),
(5,5,'Voie doublon et type de voie différent'),
(6,6,'Voie doublon avec orthographe différente'),
(7,8,'Répétition du type de voie'),
(8,9,'Nom introuvable sur le terrain'),
(9,10,'Ancien nom supprimé sur le terrain'),
(10,99,'Erreurs combinées'),
(11,15,'Adresses hors périmètre'),
(12,12,'Voie détruite'),
(13,13,'Voie incorporée à une autre'),
(14,14,'Voie inexistante'),
(15,7,'Voie doublon (même type et même nom)'),
(16,11,'Nom tronqué'),
(17,16,'Erreur de commune'),
(18,17,'FANTOIR annulé non remplacé'),
(19,18,'Point cardinal superflu'),
(20,19,'Voie en projet'),
(21,20,'Lieu-dit sur plusieurs communes'),
(22,21,'Chaussée hors commune');

CREATE TABLE IF NOT EXISTS statut_numero (
    numero text,
    fantoir character (10),
    source text,
    id_statut integer,
    timestamp_statut double precision,
    code_insee character(5));
CREATE INDEX IF NOT EXISTS idx_statut_numero_fantoir ON statut_numero(fantoir,numero);
CREATE INDEX IF NOT EXISTS idx_statut_numero_code_insee ON statut_numero(code_insee);

CREATE TABLE IF NOT EXISTS labels_statuts_numero(
    id_statut integer primary key,
    tri integer default 0,
    label_statut character varying(200)
);
TRUNCATE labels_statuts_numero;
INSERT INTO labels_statuts_numero (id_statut,tri,label_statut)
VALUES (0,0,'Ok'),
(1,1,'Adresse fictive en 5xxx'),
(2,2,'Adresse fictive en 9xxx'),
(3,3,'Adresse invisible sur le terrain'),
(4,4,'Emplacement sur une autre voie'),
(5,5,'Adresse en dehors de la commune'),
(6,6,'Adresse doublon'),
(7,7,'Adresse de lieu-dit aussi associée à une voie'),
(8,8,'Emplacement manifestement incohérent'),
(9,9,'Ancienne numérotation plus en vigueur');


DROP VIEW IF EXISTS statut_numeros;
CREATE OR REPLACE VIEW vue_statut_numeros
AS
SELECT row_number() OVER () AS gid,
       r.code_insee,
       com.libelle AS commune,
       r.uppernumero AS numero,
       b.nom_voie,
       fantoir,
       r.source,
       labels_statuts_numero.label_statut AS commentaire,
       to_timestamp(r.timestamp_statut) AS date_remontee,
       b.geometrie
 FROM  (SELECT numero,
               fantoir,
               source,
               id_statut,
               timestamp_statut,
               code_insee,
               translate(upper(numero), ' '::text, ''::text) AS uppernumero,
               rank() OVER (PARTITION BY numero, fantoir, source ORDER BY timestamp_statut DESC) AS rang
        FROM   statut_numero
        WHERE  id_statut <> 0) r
        JOIN   labels_statuts_numero
        USING  (id_statut)
        JOIN   (SELECT  geometrie,
                        fantoir,
                        nom_voie,
                        translate(upper(numero), ' '::text, ''::text) AS uppernumero
               FROM     bano_adresses
               WHERE    source = 'BAN') b
        USING  (fantoir, uppernumero)
JOIN    cog_commune com
ON      com.com = r.code_insee
WHERE   r.rang = 1;
