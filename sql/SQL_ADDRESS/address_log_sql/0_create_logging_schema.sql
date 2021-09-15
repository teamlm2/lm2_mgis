
set search_path to logging, base, public;

CREATE TABLE st_street as select 'data_address'::varchar(20) as schema, 'INS'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'ankhbold'::text, * from data_address.st_street with data;
CREATE TABLE st_road as select 'data_address'::varchar(20) as schema, 'INS'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'ankhbold'::text, * from data_address.st_road with data;

grant select on st_street, st_road to log_view;

--REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA logging FROM geodb_admin;

--grant select on ca_parcel_tbl, ca_building_tbl, ct_contract, ct_ownership_record, ct_application, ct_decision, bs_person to geodb_admin;

--GRANT SELECT, INSERT ON TABLE ca_parcel_tbl, ca_building_tbl, ct_contract, ct_ownership_record, ct_application, ct_decision, bs_person TO geodb_admin;

set search_path to logging, base, public;
DROP TRIGGER IF EXISTS st_street_log ON data_address.st_street;
CREATE TRIGGER st_street_log
  AFTER INSERT OR UPDATE OR DELETE
  ON data_address.st_street
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

DROP TRIGGER IF EXISTS st_road_log ON data_address.st_road;
CREATE TRIGGER st_road_log
  AFTER INSERT OR UPDATE OR DELETE
  ON data_address.st_road
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

