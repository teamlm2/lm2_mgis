-- Table: data_landuse.ca_landuse_type_level2_tbl

-- DROP TABLE data_landuse.ca_landuse_type_level2_tbl;

CREATE TABLE data_landuse.ca_landuse_type_level2_tbl
(
  parcel_id serial NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  landuse integer NOT NULL,
  landuse_level1 integer,
  landuse_level2 integer,
  area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  au1 character varying(3) NOT NULL,
  au2 character varying(5) NOT NULL,
  au3 character varying(8),
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  cad_parcel_id character varying(10),
  is_overlaps_historiy boolean,
  CONSTRAINT ca_landuse_type_level2_tbl_pkey PRIMARY KEY (parcel_id),
  CONSTRAINT ca_landuse_type_level2_tbl_au1_fkey FOREIGN KEY (au1)
      REFERENCES admin_units.au_level1 (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ca_landuse_type_level2_tbl_au2_fkey FOREIGN KEY (au2)
      REFERENCES admin_units.au_level2 (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ca_landuse_type_level2_tbl_cad_parcel_id_fkey FOREIGN KEY (cad_parcel_id)
      REFERENCES data_soums_union.ca_parcel_tbl (parcel_id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ca_landuse_type_level2_tbl_landuse_level1_fkey FOREIGN KEY (landuse_level1)
      REFERENCES codelists.cl_landuse_type (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ca_landuse_type_level2_tbl_landuse_level2_fkey FOREIGN KEY (landuse_level2)
      REFERENCES codelists.cl_landuse_type (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
)
WITH (
  OIDS=FALSE,
  autovacuum_enabled=true
);
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_type_level2_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type_level2_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_level2_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_level2_tbl TO reporting;

-- Index: data_landuse.idx_ca_landuse_type_level2_landuse

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_landuse;

CREATE INDEX idx_ca_landuse_type_level2_landuse
  ON data_landuse.ca_landuse_type_level2_tbl
  USING btree
  (landuse);

-- Index: data_landuse.idx_ca_landuse_type_level2_parcel_id

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_parcel_id;

CREATE INDEX idx_ca_landuse_type_level2_parcel_id
  ON data_landuse.ca_landuse_type_level2_tbl
  USING btree
  (parcel_id);

-- Index: data_landuse.idx_ca_landuse_type_level2_valid_from

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_valid_from;

CREATE INDEX idx_ca_landuse_type_level2_valid_from
  ON data_landuse.ca_landuse_type_level2_tbl
  USING btree
  (valid_from);

-- Index: data_landuse.idx_ca_landuse_type_level2_valid_till

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_valid_till;

CREATE INDEX idx_ca_landuse_type_level2_valid_till
  ON data_landuse.ca_landuse_type_level2_tbl
  USING btree
  (valid_till);

-- Index: data_landuse.st_idx_ca_landuse_type_level2_tbl

-- DROP INDEX data_landuse.st_idx_ca_landuse_type_level2_tbl;

CREATE INDEX st_idx_ca_landuse_type_level2_tbl
  ON data_landuse.ca_landuse_type_level2_tbl
  USING gist
  (geometry);


-- Trigger: landuse_type_log on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER landuse_type_log ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER landuse_type_log
  AFTER INSERT OR UPDATE OR DELETE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.log_changes();

-- Trigger: set_default_au1 on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER set_default_au1 ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

-- Trigger: set_default_au2 on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER set_default_au2 ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

-- Trigger: set_default_au3 on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER set_default_au3 ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER set_default_au3
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au3();

-- Trigger: set_default_valid_time on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER set_default_valid_time ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

-- Trigger: update_area on data_landuse.ca_landuse_type_level2_tbl

-- DROP TRIGGER update_area ON data_landuse.ca_landuse_type_level2_tbl;

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_level2_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER landuse_type_log;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER set_default_au1;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER set_default_au2;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER set_default_au3;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER set_default_valid_time;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl DISABLE TRIGGER update_area;

insert into data_landuse.ca_landuse_type_level2_tbl
select * from data_landuse.ca_landuse_type_tbl;

ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER landuse_type_log;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER set_default_au1;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER set_default_au2;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER set_default_au3;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER set_default_valid_time;
ALTER TABLE data_landuse.ca_landuse_type_level2_tbl ENABLE TRIGGER update_area;

-----------

set search_path to logging, base, public;
CREATE TABLE logging.ca_landuse_type_level2_tbl as select 'xxx'::varchar(20) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'ankhbold'::text, * from data_landuse.ca_landuse_type_level2_tbl with no data;

grant select on logging.ca_landuse_type_level2_tbl to log_view;