
set search_path to data_top, public, base, settings;

create table ca_parcel_tbl
(
parcel_id character varying(10) NOT NULL,
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
  au2 character varying(5),
  property_no text,
  org_type integer,
  au3 character varying(8),
  CONSTRAINT ca_parcel_tbl_pkey PRIMARY KEY (parcel_id),
  CONSTRAINT ca_parcel_tbl_au3_fkey FOREIGN KEY (au3)
      REFERENCES admin_units.au_level3 (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT ca_parcel_tbl_au2_fkey FOREIGN KEY (au2)
      REFERENCES admin_units.au_level2 (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX st_idx_ca_parcel_tbl
  ON ca_parcel_tbl
  USING gist
  (geometry);

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE update_area_or_length();

CREATE TRIGGER check_spatial_restriction
  BEFORE INSERT OR UPDATE
  ON ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE check_spatial_restriction();

CREATE TRIGGER a_create_parcel_id
  BEFORE INSERT
  ON ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE create_parcel_id();

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE set_default_valid_time();  

create or replace view ca_parcel as select * from ca_parcel_tbl where user in (select user_name from set_role_user) AND overlaps(valid_from, valid_till, (SELECT pa_from from set_role_user where user_name = user), (select pa_till from set_role_user where user_name = user));

grant select, insert, update, delete on ca_parcel to top_cadastre_update;
grant select on ca_parcel to top_cadastre_view, reporting;

CREATE OR REPLACE VIEW ca_refused_parcel AS
 SELECT *
   FROM ca_parcel_tbl
  WHERE ca_parcel_tbl.valid_from IS NULL OR ca_parcel_tbl.valid_till IS NULL;

GRANT SELECT ON TABLE ca_refused_parcel TO top_cadastre_update, top_cadastre_view, reporting;

create view ca_union_parcel as
  Select * from ca_parcel
  UNION ALL
    SELECT * from ca_refused_parcel;

grant select on ca_union_parcel to top_cadastre_view, top_cadastre_update, reporting;

-- ca_building
create table ca_building_tbl
(
building_id character varying(13) NOT NULL,
  building_no character varying(10),
  geo_id character varying(17),
  area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date NOT NULL DEFAULT ('now'::text)::date,
  valid_till date NOT NULL DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  au2 character varying(5),
  org_type integer,
  CONSTRAINT ca_building_tbl_pkey PRIMARY KEY (building_id),
  CONSTRAINT ca_parcel_tbl_au2_fkey FOREIGN KEY (au2)
      REFERENCES admin_units.au_level2 (code) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX st_idx_ca_building_tbl
  ON ca_building_tbl
  USING gist
  (geometry);

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON ca_building_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE update_area_or_length();

CREATE TRIGGER check_spatial_restriction
  BEFORE INSERT OR UPDATE
  ON ca_building_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE check_spatial_restriction();

 CREATE TRIGGER a_create_building_id
  BEFORE INSERT OR UPDATE
  ON ca_building_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE create_building_id();

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON ca_building_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE set_default_valid_time();  

CREATE INDEX idx_parcel_valid_from ON ca_parcel_tbl(valid_from);
CREATE INDEX idx_parcel_valid_till ON ca_parcel_tbl(valid_till);
CREATE INDEX idx_building_valid_from ON ca_building_tbl(valid_from);
CREATE INDEX idx_building_valid_till ON ca_building_tbl(valid_till);
  
create or replace view ca_building as select * from ca_building_tbl where user in (select user_name from set_role_user) AND overlaps(valid_from, valid_till, (SELECT pa_from from set_role_user where user_name = user), (select pa_till from set_role_user where user_name = user));

grant select, insert, update, delete on ca_building to top_cadastre_update;
grant select on ca_building to top_cadastre_view;