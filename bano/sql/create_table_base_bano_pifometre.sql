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
(21,20,'Lieu-dit sur plusieurs communes');

CREATE TABLE IF NOT EXISTS statut_numero (
    numero text,
    fantoir character (10),
    source text,
    id_statut integer,
    timestamp_statut double precision,
    code_insee character(5));
CREATE INDEX IF NOT EXISTS idx_statut_numero_fantoir ON statut_numero(fantoir,numero);

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
(6,6,'Adresse doublon');
