﻿--CREATE ROLE address_view;
--CREATE ROLE address_update;
--CREATE ROLE address_admin;

DROP SCHEMA IF EXISTS data_address CASCADE;
CREATE SCHEMA data_address;
GRANT USAGE ON SCHEMA data_address TO public;
SET SEARCH_PATH TO data_address, admin_units, public;

-------------
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
COMMENT ON TABLE cl_street_type
  IS 'Гудамжны төрөл';

insert into data_address.cl_street_type values (1, 'Өргөн чөлөө', null);
insert into data_address.cl_street_type values (2, 'Тойруу/тойрог', null);
insert into data_address.cl_street_type values (3, 'Гол гудамж', null);
insert into data_address.cl_street_type values (4, 'Туслах гудамж', null);
insert into data_address.cl_street_type values (5, 'Бусад', null);

-------------
DROP TABLE if exists  data_address.st_road cascade;
CREATE TABLE st_road
(
    id BIGSERIAL PRIMARY KEY,
	code varchar(250),
	name varchar(250),
	name_en varchar(250),
	description text,
	is_active boolean not null DEFAULT false,
	in_source int references data_address.cl_address_source on update cascade on delete restrict,
	road_type_id int references data_address.cl_road_type on update cascade on delete restrict,
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
	au3 text
);
grant select, insert, update, delete on st_road to address_update;
grant select on st_road to address_view;

CREATE INDEX st_road_geometry_idx ON st_road USING GIST(geometry);
CREATE INDEX st_road_road_type_id_idx ON st_road(road_type_id);

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
	valid_from date DEFAULT ('now'::text)::date,
    valid_till date DEFAULT 'infinity'::date,
	geometry geometry(MULTIPOLYGON, 4326),
	area_m2 numeric,
	line_geom geometry(MultiLineString,4326),
	length numeric,
	created_by integer,
    updated_by integer,
    created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
    updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
	au1 varchar(3) references admin_units.au_level1 on update cascade on delete restrict,
	au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
	au3 text
);
grant select, insert, update, delete on st_street to address_update;
grant select on st_street to address_view;

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
	parcel_id varchar(10) references data_soums_union.ca_parcel_tbl on update cascade on delete restrict,
	is_active boolean not null DEFAULT false,
	in_source int references data_address.cl_address_source on update cascade on delete restrict,
	zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
	street_id int references data_address.st_street on update cascade on delete restrict,
    address_parcel_no VARCHAR(64),
	address_streetname character varying(250),
	address_neighbourhood character varying(250),
	geographic_name character varying(250),
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
	parcel_id varchar(10) references data_soums_union.ca_parcel_tbl on update cascade on delete restrict,
	building_id varchar(13) references data_soums_union.ca_building_tbl on update cascade on delete restrict,
	is_active boolean not null DEFAULT false,
	building_name text,
	in_source int references data_address.cl_address_source on update cascade on delete restrict,
	zipcode_id int references data_address.au_zipcode_area on update cascade on delete restrict,
	street_id int references data_address.st_street on update cascade on delete restrict,
	address_parcel_no VARCHAR(64),
	address_streetname character varying(250),
    address_building_no VARCHAR(64),	
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
  IS 'Нэгж талбарын хаяг';
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