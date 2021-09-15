set search_path to data_landuse, public;
DROP TABLE if exists data_landuse.ca_landuse_type1_tbl;

CREATE TABLE data_landuse.ca_landuse_type1_tbl
(
  parcel_id serial,
  old_parcel_id character varying(14),
  geo_id character varying(17),
  landuse integer,
  area_m2 numeric,
  documented_area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  old_address_khashaa character varying(64),
  old_address_streetname character varying(250),
  landuse_level1 integer,
  landuse_level2 integer,
  CONSTRAINT ca_landuse_type1_tbl_pkey PRIMARY KEY (parcel_id),
  CONSTRAINT ca_landuse_type1_tbl_landuse_fkey FOREIGN KEY (landuse)
      REFERENCES codelists.cl_landuse_type (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_type1_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_type1_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type1_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type1_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type1_tbl TO reporting;

CREATE INDEX idx_ca_landuse_type1_parcel_id
  ON data_landuse.ca_landuse_type1_tbl
  USING btree
  (parcel_id);

CREATE INDEX idx_ca_landuse_type1_landuse
  ON data_landuse.ca_landuse_type1_tbl
  USING btree
  (landuse);

CREATE INDEX idx_ca_landuse_type1_valid_from
  ON data_landuse.ca_landuse_type1_tbl
  USING btree
  (valid_from);

CREATE INDEX idx_ca_landuse_type1_valid_till
  ON data_landuse.ca_landuse_type1_tbl
  USING btree
  (valid_till);

CREATE INDEX st_idx_ca_landuse_type1_tbl
  ON data_landuse.ca_landuse_type1_tbl
  USING gist
  (geometry);

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type1_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type1_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();