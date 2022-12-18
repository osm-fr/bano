CREATE TABLE IF NOT EXISTS topo (
                            code_dep         character(3),
                            code_insee       character(5),
                            fantoir10        character(10),
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
CREATE INDEX IF NOT EXISTS idx_topo_fantoir10  ON topo(fantoir10);

CREATE TABLE IF NOT EXISTS ban (
    id text,
    id_fantoir text,
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
    cad_parcelles text);
--    geometrie geometry (Point, 4326) DEFAULT (ST_Point(lon,lat)));
CREATE INDEX IF NOT EXISTS idx_ban_code_insee ON ban(code_insee);

CREATE TABLE IF NOT EXISTS lieux_dits (
    insee_com character(5),
    nom text,
    created date,
    updated date,
    geometrie geometry(Polygon,4326));

CREATE INDEX IF NOT EXISTS gidx_lieux_dits ON lieux_dits USING gist(geometrie);
CREATE INDEX IF NOT EXISTS lieux_dits_insee_com ON lieux_dits (insee_com);

CREATE TABLE IF NOT EXISTS suffixe (
                geometrie               geometry,
                code_insee              character(5),
                libelle_suffixe character varying(100)
);
CREATE INDEX IF NOT EXISTS gidx_suffixe ON suffixe USING GIST(geometrie);
CREATE INDEX IF NOT EXISTS idx_suffixe ON suffixe(code_insee);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO public;