DROP TABLE IF EXISTS 	fantoir_voie	CASCADE;
CREATE TABLE fantoir_voie (	code_dept		character(2),
							code_dir		character(1),
							code_com		character(3),
							code_insee		character(5),
							id_voie			character(4),
							cle_rivoli		character(1),
							nature_voie		character varying(4),
							libelle_voie	character varying(26),
							type_commune	character(1),
							caractere_rur	character(1),
							caractere_voie	character(1),
							caractere_pop	character(1),
							pop_a_part		integer,
							pop_fictive		integer,
							caractere_annul	character(1),
							date_annul		character varying(9),
							date_creation	character varying(9),
							code_majic		character(5),
							type_voie		character(1),
							lieud_dit_bati	character(1),
							dernier_mot		character varying(8));
CREATE INDEX idx_fantoir_voie_dept
ON				fantoir_voie(code_dept);
CREATE INDEX idx_fantoir_code_insee
ON				fantoir_voie(code_insee);