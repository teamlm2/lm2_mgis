﻿--CREATE ROLE address_view;
--CREATE ROLE address_update;
--CREATE ROLE address_admin;

DROP SCHEMA IF EXISTS data_address CASCADE;
CREATE SCHEMA data_address;
GRANT USAGE ON SCHEMA data_address TO public;
SET SEARCH_PATH TO data_address, admin_units, public;

-------------
set search_path to data_address;
DROP TABLE if exists  data_address.cl_address_status cascade;
CREATE TABLE cl_address_status
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75)
);
grant select, insert, update, delete on cl_address_status to address_admin;
grant select on cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE cl_address_status
  IS 'Хаягийн төлөв';

insert into data_address.cl_address_status values (1, 'Урьдчилсан хаяг', null);
insert into data_address.cl_address_status values (2, 'Баталгаажсан хаяг', null);

------------

DROP TABLE if exists  data_address.cl_address_source cascade;
CREATE TABLE cl_address_source
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75),
  source_type varchar(100)
);
grant select, insert, update, delete on cl_address_source to address_admin;
grant select on cl_address_source to address_view;
grant select on cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE cl_address_source
  IS 'Хаягийн мэдээллийн эх сурвалж';

insert into data_address.cl_address_source values (1, 'Кадастрын мэдээллийн сангийн бүртгэл', null, 'address');
insert into data_address.cl_address_source values (2, 'Хаягийн мэдээллийн сангийн бүртгэл', null, 'address');
insert into data_address.cl_address_source values (3, 'Үндэсний статистикийн хорооны бүртгэл', null, 'address');
insert into data_address.cl_address_source values (4, 'Хот төлөвлөлт ерөнхий төлөвлөгөөний газрын бүртгэл', null, 'address');
insert into data_address.cl_address_source values (5, 'Улсын бүртгэлийн ерөнхий газрын бүртгэл', null, 'address');
insert into data_address.cl_address_source values (6, 'Зам тээврийн газар', null, 'road');

insert into data_address.cl_address_source values (8, 'Бусад', '');

-------------
DROP TABLE if exists  data_address.cl_road_type cascade;
CREATE TABLE cl_road_type
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75),
  max_value int,
  min_value int
);
grant select, insert, update, delete on cl_road_type to address_admin;
grant select on cl_road_type to address_view;
grant select on cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE cl_road_type
  IS 'Замын төрөл';
  

insert into data_address.cl_road_type values (1, 'Аж ахуйн нэгж, байгууллагын дотоодын авто зам', null, null);
insert into data_address.cl_road_type values (2, 'Тусгай зориулалтын авто зам', null, null);
insert into data_address.cl_road_type values (3, 'Нийслэлийн авто зам', null, null);
insert into data_address.cl_road_type values (4, 'Орон нутгийн чанартай авто зам', null, null);
insert into data_address.cl_road_type values (5, 'Улсын чанартай авто зам', null, null);
insert into data_address.cl_road_type values (6, 'Олон улсын чанартай авто зам', null, null);

-------------
DROP TABLE if exists  data_address.cl_street_type cascade;
CREATE TABLE cl_street_type
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75)
);
grant select, insert, update, delete on cl_street_type to address_admin;
grant select on cl_street_type to address_view;
grant select on cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE cl_street_type
  IS 'Гудамжны төрөл';

insert into data_address.cl_street_type values (1, 'Өргөн чөлөө', null);
insert into data_address.cl_street_type values (2, 'Тойруу/тойрог', null);
insert into data_address.cl_street_type values (3, 'Гол гудамж', null);
insert into data_address.cl_street_type values (4, 'Туслах гудамж', null);
insert into data_address.cl_street_type values (5, 'Бусад', null);

-------------

DROP TABLE if exists  data_address.cl_street_shape cascade;
CREATE TABLE data_address.cl_street_shape
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75)
);
grant select, insert, update, delete on data_address.cl_street_shape to address_admin;
grant select, insert, update, delete on data_address.cl_street_shape to cadastre_update;
grant select on data_address.cl_street_shape to address_view;
grant select on data_address.cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE data_address.cl_street_shape
  IS 'Гудамжны хэлбэр';

insert into data_address.cl_street_shape values (1, 'Тойрог', null);
insert into data_address.cl_street_shape values (2, 'Шулуун', null);
insert into data_address.cl_street_shape values (3, 'Цогцолбор', null);


-------------

DROP TABLE if exists  data_address.cl_entry_type cascade;
CREATE TABLE data_address.cl_entry_type
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75)
);
grant select, insert, update, delete on data_address.cl_entry_type to address_admin;
grant select on data_address.cl_entry_type to address_view;
grant select on cl_address_status to address_view, cadastre_view;
COMMENT ON TABLE data_address.cl_entry_type
  IS 'Хаягийн орц, гарцын төрөл';

insert into data_address.cl_entry_type values (1, 'орц, гарц', null);
insert into data_address.cl_entry_type values (2, 'зөвхөн орц', null);
insert into data_address.cl_entry_type values (3, 'зөвхөн гарц');

-------------
DROP TABLE if exists  data_address.st_road cascade;
CREATE TABLE data_address.st_road
(
id BIGSERIAL PRIMARY KEY,
code varchar(250),
name varchar(250),
name_en varchar(250),
description text,
street_sub_id int references data_address.st_street_sub on update cascade on delete restrict,
street_id int references data_address.st_sub on update cascade on delete restrict,
source integer,
target integer,
is_active boolean not null DEFAULT false,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
road_type_id int references data_address.cl_road_type on update cascade on delete restrict,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
geometry geometry(POLYGON, 4326),
area_m2 numeric,
line_geom geometry(LineString,4326),
length numeric,
max_speed integer;
lanes integer;
surface text;
highway text;
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 text
);
GRANT ALL ON TABLE data_address.st_road TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_road TO address_update;
GRANT SELECT ON TABLE data_address.st_road TO address_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_road TO cadastre_update;

CREATE INDEX st_road_geometry_idx ON data_address.st_road USING GIST(geometry);
CREATE INDEX st_road_road_type_id_idx ON data_address.st_road(road_type_id);

-------------
DROP TABLE if exists  data_address.st_street cascade;
CREATE TABLE st_street
(
id BIGSERIAL PRIMARY KEY,
code varchar(250),
name varchar(250),
name_en varchar(250),
description text,
decision_date date,
decision_no varchar(20),
decision_level_id int references data_plan.cl_plan_decision_level on update cascade on delete restrict,
is_active boolean not null DEFAULT false,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
street_type_id int references data_address.cl_street_type on update cascade on delete restrict,
street_shape_id int references data_address.cl_street_shape on update cascade on delete restrict,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
geometry geometry(MULTIPOLYGON, 4326),
area_m2 numeric,
line_geom geometry(MultiLineString,4326),
length numeric,
is_marked boolean,
parent_id bigint,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
start_number int,
end_number int,
building_start_number int,
building_end_number int,
current_number int,
parcel_numbering_space int,
building_numbering_space int,
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 text
);
grant select, insert, update, delete on st_street to address_update;
grant select on st_street to address_view;

ALTER TABLE data_address.st_street ADD CONSTRAINT st_street_unique UNIQUE (code, name, parent_id);

CREATE INDEX st_street_geometry_idx ON st_street USING GIST(geometry);
CREATE INDEX st_street_street_type_id_idx ON st_street(street_type_id);

DROP TABLE if exists  data_address.st_street_sub cascade;
CREATE TABLE st_street_sub
(
id BIGSERIAL PRIMARY KEY,
code varchar(250),
name varchar(250),
name_en varchar(250),
description text,
is_active boolean not null DEFAULT false,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
street_type_id int references data_address.cl_street_type on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
geometry geometry(POLYGON, 4326),
area_m2 numeric,
line_geom geometry(MultiLineString,4326),
length numeric,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 text,
unique (au2, street_id, code)
);
grant select, insert, update, delete on st_street to address_update;
grant select on st_street to address_view;

CREATE INDEX st_street_sub_geometry_idx ON st_street USING GIST(geometry);
CREATE INDEX st_street_street_sub_type_id_idx ON st_street(street_type_id);

-------------

CREATE TABLE ca_parcel_address
(
id BIGSERIAL PRIMARY KEY,
parcel_id text,
is_active boolean not null DEFAULT false,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict,
status int references data_address.cl_address_status on update cascade on delete restrict,
address_parcel_no VARCHAR(64),
address_streetname character varying(250),
address_neighbourhood character varying(250),
geographic_name character varying(250),
description text,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
is_marked boolean,
area_m2 numeric,
geometry geometry(Polygon,4326),
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 varchar(8) references admin_units.au_level3 on update cascade on delete restrict,
khoroolol_id int references admin_units.au_khoroolol on update cascade on delete restrict,
sort_value int,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now()
);
COMMENT ON TABLE ca_parcel_address
  IS 'Нэгж талбарын хаяг';
grant select, insert, update, delete on ca_parcel_address to address_update;
grant select on ca_parcel_address to address_view;

CREATE INDEX ca_parcel_address_parcel_id_idx ON ca_parcel_address(parcel_id);

--------------

CREATE TABLE ca_building_address
(
id BIGSERIAL PRIMARY KEY,
parcel_id text,
building_id text,
is_active boolean not null DEFAULT false,
building_name text,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict,
status int references data_address.cl_address_status on update cascade on delete restrict,
address_parcel_no VARCHAR(64),
address_streetname character varying(250),
address_building_no VARCHAR(64),
is_marked boolean,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
area_m2 numeric,
geometry geometry(Polygon,4326),
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 varchar(8) references admin_units.au_level3 on update cascade on delete restrict,
khoroolol_id int references admin_units.au_khoroolol on update cascade on delete restrict,
sort_value int,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now()
);
COMMENT ON TABLE ca_building_address
  IS 'Барилгын хаяг';
grant select, insert, update, delete on ca_building_address to address_update;
grant select on ca_building_address to address_view;

CREATE INDEX ca_building_address_parcel_id_idx ON ca_building_address(building_id);

------------

CREATE TABLE au_zipcode_area
(
  id serial primary key,
  code integer NOT NULL,
  description character varying(500),
  area_m2 numeric(13,2),
  geometry geometry(MultiPolygon,4326)
);
grant select, insert, update, delete on au_zipcode_area to address_admin;
grant select on au_zipcode_area to address_view;
COMMENT ON TABLE au_zipcode_area
  IS 'Шуудангийн бүсчлэл';
  
CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_address.au_zipcode_area
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

DROP TABLE if exists  data_address.st_entrance cascade;
CREATE TABLE data_address.st_entrance
(
entrance_id varchar(20) PRIMARY KEY,
code varchar(250),
name varchar(250),
type int references data_address.cl_entry_type on update cascade on delete restrict,
address_entry_no character varying(10) not null,
description text,
is_active boolean not null DEFAULT true,
building_id int references data_address.ca_building_address on update cascade on delete restrict,
parcel_id int references data_address.ca_parcel_address on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
address_parcel_no character varying(64),
address_streetname character varying(250),
address_neighbourhood character varying(250),
geographic_name character varying(250),
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
geometry geometry(POINT, 4326),	
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 varchar(8) references admin_units.au_level3 on update cascade on delete restrict
);
grant select, insert, update, delete on data_address.st_entrance to address_update;
grant select on data_address.st_entrance to address_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_entrance TO cadastre_update;
GRANT SELECT ON TABLE data_address.st_entrance TO cadastre_view;

CREATE INDEX st_entrance_geometry_idx ON data_address.st_entrance USING GIST(geometry);
CREATE INDEX st_entrance_road_type_id_idx ON data_address.st_entrance(entrance_id);

------------
DROP TABLE if exists data_address.st_street_point;
CREATE TABLE data_address.st_street_point
(
  id bigserial primary key,
  is_active boolean NOT NULL DEFAULT true,
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Point,4326),
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  au1 character varying(3),
  au2 character varying(5),
  au3 text
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.st_street_point
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_point TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_street_point TO reporting;
GRANT SELECT ON TABLE data_address.st_street_point TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_street_point TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_street_point TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_street_point TO cadastre_update;

---------------
DROP TABLE if exists data_address.st_map_street_point CASCADE ;
CREATE TABLE data_address.st_map_street_point
(
id serial primary key,
street_point_id int references data_address.st_street_point on update cascade on delete restrict not null,
street_id int references data_address.st_street on update cascade on delete restrict not null,
type int,
unique(street_id, street_point_id, type)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.st_map_street_point
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_map_street_point TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_map_street_point TO reporting;
GRANT SELECT ON TABLE data_address.st_map_street_point TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_map_street_point TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_map_street_point TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_map_street_point TO cadastre_update;

GRANT ALL ON SEQUENCE data_address.st_map_street_point_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_address.st_map_street_point_id_seq TO cadastre_view;
GRANT USAGE ON SEQUENCE data_address.st_map_street_point_id_seq TO cadastre_update;

------

set search_path to data_address;

drop table if exists ca_parcel_address_history cascade;
CREATE TABLE ca_parcel_address_history
(
id BIGSERIAL PRIMARY KEY,
parcel_id int references data_address.ca_parcel_address on update cascade on delete restrict,
is_active boolean not null DEFAULT false,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
address_parcel_no VARCHAR(64),
address_street_code character varying(250),
address_streetname character varying(250),
address_neighbourhood character varying(250),
geographic_name character varying(250),
description text,
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 varchar(8) references admin_units.au_level3 on update cascade on delete restrict,
khoroolol_id int references admin_units.au_khoroolol on update cascade on delete restrict,
sort_value int,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now()
);
COMMENT ON TABLE ca_parcel_address_history
  IS 'Нэгж талбарын хаягийн түүх';
grant select, insert, update, delete on ca_parcel_address_history to address_update;
grant select on ca_parcel_address_history to address_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_history TO cadastre_update;
GRANT SELECT ON TABLE data_address.ca_parcel_address_history TO cadastre_view;

CREATE INDEX ca_parcel_address_history_parcel_id_idx ON ca_parcel_address_history(parcel_id);

------------
drop table if exists ca_building_address_history cascade;
CREATE TABLE ca_building_address_history
(
id BIGSERIAL PRIMARY KEY,
building_id int references data_address.ca_building_address on update cascade on delete restrict,
is_active boolean not null DEFAULT false,
building_name text,
in_source int references data_address.cl_address_source on update cascade on delete restrict,
zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
street_id int references data_address.st_street on update cascade on delete restrict,
address_parcel_no VARCHAR(64),
address_street_code character varying(250),
address_streetname character varying(250),
address_building_no VARCHAR(64),
valid_from date DEFAULT ('now'::text)::date,
valid_till date DEFAULT 'infinity'::date,
au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
au3 varchar(8) references admin_units.au_level3 on update cascade on delete restrict,
khoroolol_id int references admin_units.au_khoroolol on update cascade on delete restrict,
sort_value int,
created_by integer,
updated_by integer,
created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
updated_at timestamp(0) without time zone NOT NULL DEFAULT now()
);
COMMENT ON TABLE ca_building_address_history
  IS 'Барилгын хаягийн түүх';
grant select, insert, update, delete on ca_building_address_history to address_update;
grant select on ca_building_address_history to address_view;

CREATE INDEX ca_building_address_history_parcel_id_idx ON ca_building_address_history(building_id);

------------
set search_path to data_address;

DROP TABLE if exists  data_address.cl_building_purpose cascade;
CREATE TABLE cl_building_purpose
(
  id serial  primary key,
  code integer,
  description character varying(256) NOT NULL UNIQUE,
  shortname character varying(256),
  description_en character varying(256),
  is_special boolean NOT NULL DEFAULT false
);
grant select, insert, update, delete on cl_building_purpose to address_admin;
grant select on cl_building_purpose to address_view;
grant select on cl_address_status to address_view, cadastre_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_contract_type TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_contract_type TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_contract_type TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_contract_type TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_contract_type TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_contract_type TO reporting;

COMMENT ON TABLE cl_building_purpose
  IS 'Барилгын зориулалт';
  
---------------
set search_path to data_address;

CREATE TABLE data_address.cl_address_document_type
(
  document_type_id serial PRIMARY KEY,
  code character varying(10) NOT NULL,
  description character varying(255) NOT NULL,
  description_en character varying(255),
  is_required boolean NOT NULL,
  type character varying(50),
  is_active boolean NOT NULL,
  created_at timestamp without time zone,
  created_by character varying(50),
  updated_at timestamp without time zone,
  updated_by character varying(50),
  is_multiple boolean,
  is_public_show boolean DEFAULT true,
  is_delete boolean DEFAULT true
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.cl_address_document_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.cl_address_document_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.cl_address_document_type TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.cl_address_document_type TO application_update;
GRANT SELECT, INSERT ON TABLE data_address.cl_address_document_type TO cadastre_view;

insert into data_address.cl_address_document_type(code, description, is_required, type, is_active, is_multiple, is_public_show, is_delete) values('01', 'ИТХ-н тогтоол', true, 'pdf', true, true, true, true);
insert into data_address.cl_address_document_type(code, description, is_required, type, is_active, is_multiple, is_public_show, is_delete) values('01', 'Тэмдэглэгээ хийсэн зураг', true, 'pdf', true, true, true, true);


CREATE TABLE data_address.st_document
(
  document_id serial PRIMARY KEY,
  name character varying(100) NOT NULL,
  file_url character varying(500) NOT NULL,
  description text,
  ftp_id integer NOT NULL,
  created_at timestamp without time zone,
  created_by integer,
  updated_at timestamp without time zone,
  updated_by integer,
  document_type_id int references data_address.cl_address_document_type on update cascade on delete restrict
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.st_document
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_document TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_document TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_document TO application_update;
GRANT SELECT, INSERT ON TABLE data_address.st_document TO cadastre_view;

------

CREATE TABLE data_address.st_street_document
(
  document_id integer NOT NULL,
  street_id int references data_address.st_street on update cascade on delete restrict,
  created_at timestamp without time zone,
  created_by integer,
  document_type_id int references data_address.cl_address_document_type on update cascade on delete restrict,
  CONSTRAINT "PK_st_street_document" PRIMARY KEY (document_id, street_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.st_street_document
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_document TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_street_document TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_street_document TO application_update;
GRANT SELECT, INSERT ON TABLE data_address.st_street_document TO cadastre_view;

-------------
drop table if exists data_address.au_settlement_zone_point;
CREATE TABLE data_address.au_settlement_zone_point
(
  id bigserial NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Point,4326),
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  au1 character varying(3),
  au2 character varying(5),
  au3 text,
  CONSTRAINT au_settlement_zone_point_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.au_settlement_zone_point
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.au_settlement_zone_point TO geodb_admin;
GRANT SELECT ON TABLE data_address.au_settlement_zone_point TO reporting;
GRANT SELECT ON TABLE data_address.au_settlement_zone_point TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.au_settlement_zone_point TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.au_settlement_zone_point TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.au_settlement_zone_point TO cadastre_update;

GRANT ALL ON SEQUENCE data_address.au_settlement_zone_point_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_address.au_settlement_zone_point_id_seq TO cadastre_view;
GRANT USAGE ON SEQUENCE data_address.au_settlement_zone_point_id_seq TO cadastre_update;