CREATE TABLE IF NOT EXISTS bano_adresses (
    fantoir text,
    lon float,
    lat float,
    numero  text,
    nom_voie text,
    nom_place text,
    code_postal text,
    code_insee text,
    code_insee_ancienne_commune text,
    nom_ancienne_commune text,
    source text,
    certification_commune integer,
    geometrie geometry (Point, 4326) GENERATED ALWAYS AS (ST_Point(lon,lat)) STORED);

CREATE INDEX IF NOT EXISTS gidx_bano_adresses ON bano_adresses USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS idx_bano_adresses_code_insee ON bano_adresses (code_insee);

CREATE TABLE IF NOT EXISTS nom_fantoir (
    fantoir text,
    nom text,
    code_insee text,
    nature text,
    source text);

CREATE INDEX IF NOT EXISTS idx_nom_fantoir_code_insee ON nom_fantoir (code_insee);
CREATE INDEX IF NOT EXISTS idx_nom_fantoir_code_insee_source ON nom_fantoir (code_insee,source);


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