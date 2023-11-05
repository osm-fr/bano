CREATE TABLE IF NOT EXISTS topo (
                            code_dep         character(3),
                            code_insee       character(5),
                            fantoir          character(9),
                            nature_voie      text,
                            libelle_voie     text,
                            caractere_voie   character(1),
                            caractere_annul  character(1),
                            date_annul       integer,
                            date_creation    integer,
                            type_voie        character(1),
                            mot_classant     character varying(8));
CREATE INDEX IF NOT EXISTS idx_topo_dep  ON topo(code_dep);
CREATE INDEX IF NOT EXISTS idx_topo_code_insee ON topo(code_insee);
CREATE INDEX IF NOT EXISTS idx_topo_fantoir  ON topo(fantoir);

CREATE TABLE IF NOT EXISTS ban (
    id text,
    id_ban_adresse text,
    id_ban_toponyme text,
    id_ban_district text,
    id_fantoir text,
    fantoir text GENERATED ALWAYS AS (substr(id_fantoir,0,6)||substr(id_fantoir,7,10)) STORED,
    numero  text,
    rep text,
    nom_voie text,
    code_postal text,
    code_insee text,
    nom_commune text,
    code_insee_ancienne_commune text,
    nom_ancienne_commune text,
    x float,
    y float,
    lon float,
    lat float,
    type_position text,
    alias text,
    nom_ld text,
    libelle_acheminement text,
    nom_afnor text,
    source_position text,
    source_nom_voie text,
    certification_commune integer,
    cad_parcelles text,
    geometrie geometry (Point, 4326) GENERATED ALWAYS AS (ST_Point(lon,lat)) STORED);

CREATE INDEX IF NOT EXISTS idx_ban_code_insee ON ban(code_insee);
CREATE INDEX IF NOT EXISTS idx_ban_fantoir ON ban(fantoir);
CREATE INDEX IF NOT EXISTS gidx_ban ON ban(geometrie);

CREATE TABLE IF NOT EXISTS lieux_dits (
    code_insee character(5),
    nom text,
    created date,
    updated date,
    geometrie geometry(Polygon,4326),
    geom_centroid geometry (Point, 4326) GENERATED ALWAYS AS (ST_Centroid(geometrie)) STORED);

CREATE INDEX IF NOT EXISTS gidx__centroid_lieux_dits ON lieux_dits USING gist(geom_centroid);
CREATE INDEX IF NOT EXISTS lieux_dits_code_insee ON lieux_dits (code_insee);

CREATE TABLE IF NOT EXISTS suffixe (
                geometrie               geometry,
                code_insee              character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX IF NOT EXISTS gidx_suffixe ON suffixe USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS idx_suffixe ON suffixe(code_insee);

CREATE TABLE IF NOT EXISTS communes_summary (
        reg character varying(3),
        dep character varying(3),
        code_insee character(5),
        libelle text,
        population integer,
        id_revision text,
        date_revision text,
        type_composition text,
        nb_lieux_dits integer,
        nb_voies integer,
        nb_numeros integer,
        nb_numeros_certifies integer,
        analyse_adressage_nb_adresses_attendues integer,
        analyse_adressage_ratio float,
        analyse_adressage_deficit_adresses float,
        composed_at text);

CREATE INDEX IF NOT EXISTS communes_summary_code_insee ON communes_summary (code_insee);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO public;