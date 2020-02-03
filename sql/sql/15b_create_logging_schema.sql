﻿drop schema if exists logging cascade;
create schema logging;
grant usage on schema logging to public;

set search_path to logging, base, public;

CREATE TABLE ca_parcel_tbl as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ca_parcel with no data;

CREATE TABLE ca_building_tbl as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ca_building with no data;

CREATE TABLE ct_application as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ct_application with no data;

CREATE TABLE ct_contract as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ct_contract with no data;

CREATE TABLE ct_ownership_record as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ct_ownership_record with no data;

CREATE TABLE bs_person as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from base.bs_person with no data;

CREATE TABLE ct_decision as select 'xxx'::varchar(6) as schema, 'DEL'::varchar(3) as operation, '2011-01-01'::timestamp without time zone as stamp, 'user000001'::text, * from data_soums_union.ct_decision with no data;




CREATE OR REPLACE FUNCTION base.log_changes()
  RETURNS trigger AS
$BODY$
BEGIN
	IF (TG_OP = 'DELETE') THEN
		EXECUTE 'INSERT INTO logging.' || TG_TABLE_NAME || ' SELECT ' || quote_literal(TG_TABLE_SCHEMA) || ', ' || quote_literal('DEL') || ', now(), session_user, $1.*' using OLD;
	ELSIF (TG_OP = 'UPDATE') THEN
		EXECUTE 'INSERT INTO logging.' || TG_TABLE_NAME || ' SELECT ' || quote_literal(TG_TABLE_SCHEMA) || ', ' || quote_literal('OLD') || ', now(), session_user, $1.*' using OLD;
		EXECUTE 'INSERT INTO logging.' || TG_TABLE_NAME || ' SELECT ' || quote_literal(TG_TABLE_SCHEMA) || ', ' || quote_literal('NEW') || ', now(), session_user, $1.*' using NEW;
	ELSIF (TG_OP = 'INSERT') THEN
		EXECUTE 'INSERT INTO logging.' || TG_TABLE_NAME || ' SELECT ' || quote_literal(TG_TABLE_SCHEMA) || ', ' || quote_literal('INS') || ', now(), session_user, $1.*' using NEW;
	END IF;
	RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;

grant select on ca_parcel_tbl, ca_building_tbl, ct_contract, ct_ownership_record, ct_application, ct_decision, bs_person to log_view;


