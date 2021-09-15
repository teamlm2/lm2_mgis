DROP TABLE if exists data_landuse.ca_base_landuse_type_tbl;
create table data_landuse.ca_base_landuse_type_tbl as
  select * from data_landuse.ca_landuse_type_tbl
with data;

GRANT ALL ON TABLE data_landuse.ca_base_landuse_type_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_base_landuse_type_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_base_landuse_type_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_base_landuse_type_tbl TO reporting;

-- Index: data_landuse.idx_ca_landuse_type_level2_landuse

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_landuse;

CREATE INDEX idx_ca_landuse_type_level2_landuse
  ON data_landuse.ca_base_landuse_type_tbl
  USING btree
  (landuse);

-- Index: data_landuse.idx_ca_landuse_type_level2_parcel_id

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_parcel_id;

CREATE INDEX idx_ca_landuse_type_level2_parcel_id
  ON data_landuse.ca_base_landuse_type_tbl
  USING btree
  (parcel_id);

-- Index: data_landuse.idx_ca_landuse_type_level2_valid_from

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_valid_from;

CREATE INDEX idx_ca_landuse_type_level2_valid_from
  ON data_landuse.ca_base_landuse_type_tbl
  USING btree
  (valid_from);

-- Index: data_landuse.idx_ca_landuse_type_level2_valid_till

-- DROP INDEX data_landuse.idx_ca_landuse_type_level2_valid_till;

CREATE INDEX idx_ca_landuse_type_level2_valid_till
  ON data_landuse.ca_base_landuse_type_tbl
  USING btree
  (valid_till);

-- Index: data_landuse.st_idx_ca_base_landuse_type_tbl

-- DROP INDEX data_landuse.st_idx_ca_base_landuse_type_tbl;

CREATE INDEX st_idx_ca_base_landuse_type_tbl
  ON data_landuse.ca_base_landuse_type_tbl
  USING gist
  (geometry);


-- Trigger: landuse_type_log on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER landuse_type_log ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER landuse_type_log
  AFTER INSERT OR UPDATE OR DELETE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.log_changes();

-- Trigger: set_default_au1 on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER set_default_au1 ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

-- Trigger: set_default_au2 on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER set_default_au2 ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

-- Trigger: set_default_au3 on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER set_default_au3 ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER set_default_au3
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au3();

-- Trigger: set_default_valid_time on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER set_default_valid_time ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

-- Trigger: update_area on data_landuse.ca_base_landuse_type_tbl

-- DROP TRIGGER update_area ON data_landuse.ca_base_landuse_type_tbl;

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_base_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER landuse_type_log;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER set_default_au1;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER set_default_au2;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER set_default_au3;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER set_default_valid_time;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl DISABLE TRIGGER update_area;

insert into data_landuse.ca_base_landuse_type_tbl
select * from data_landuse.ca_landuse_type_tbl;

ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER landuse_type_log;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER set_default_au1;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER set_default_au2;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER set_default_au3;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER set_default_valid_time;
ALTER TABLE data_landuse.ca_base_landuse_type_tbl ENABLE TRIGGER update_area;

-----------

set search_path to logging, base, public;
CREATE TABLE logging.ca_base_landuse_type_tbl as select 'xxx'::varchar(20) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'ankhbold'::text, * from data_landuse.ca_base_landuse_type_tbl with no data;

grant select on logging.ca_base_landuse_type_tbl to log_view;

