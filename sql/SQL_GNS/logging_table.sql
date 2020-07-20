DROP TABLE logging.ca_landuse_type_tbl;

CREATE TABLE logging.ca_landuse_type_tbl
(
  schema character varying(20),
  operation character varying(3),
  stamp timestamp without time zone,
  text text,
  parcel_id integer,
  is_active boolean,
  landuse integer,
  landuse_level1 integer,
  landuse_level2 integer,
  area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date,
  valid_till date,
  geometry geometry(Polygon,4326),
  au1 character varying(3),
  au2 character varying(5),
  au3 character varying(8),
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone,
  updated_at timestamp(0) without time zone,
  cad_parcel_id varchar(10)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE logging.ca_landuse_type_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE logging.ca_landuse_type_tbl TO geodb_admin;

----
DROP TRIGGER if exists landuse_type_log ON data_landuse.ca_landuse_type_tbl;

CREATE TRIGGER landuse_type_log
  AFTER INSERT OR UPDATE OR DELETE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.log_changes();