
CREATE TABLE IF NOT EXISTS batch (
    id_batch        serial,
    etape           text,
    source          text,
    timestamp_debut bigint,
    date_debut      text,
    date_fin        text,
    duree           integer,
    code_zone       text,
    nom_zone        text,
    ok              boolean,
    CONSTRAINT batch_pkey PRIMARY KEY (id_batch));

CREATE TABLE IF NOT EXISTS batch_historique(
    id_batch        integer,
    etape           text,
    source          text,
    timestamp_debut bigint,
    date_debut      text,
    date_fin        text,
    duree           integer,
    code_zone       text,
    nom_zone        text,
    ok              boolean);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO public;