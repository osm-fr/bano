SELECT code_dept,
       code_insee,
	fantoir,
	nature_voie,
	libelle_voie,
	caractere_voie,
	TRIM (both FROM caractere_annul),
	CASE date_annul
	    WHEN '0000000' then 0
	    ELSE to_char(to_timestamp(date_annul::text, 'YYYYDDD'),'YYYYMMDD')::integer
	END,
	TO_CHAR(TO_TIMESTAMP(date_creation::text,'YYYYDDD'),'YYYYMMDD')::integer,
       type_voie,
	dernier_mot 
FROM   fantoir_voie;
