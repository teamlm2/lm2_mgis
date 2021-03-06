﻿DROP TABLE if exists data_landuse.ca_landuse_type_tbl;
CREATE TABLE data_landuse.ca_landuse_type_tbl
(
  parcel_id serial PRIMARY KEY,
  is_active boolean not null DEFAULT true,
  landuse int references codelists.cl_landuse_type on update cascade on delete restrict NOT NULL,
  landuse_level1 int references codelists.cl_landuse_type on update cascade on delete restrict NOT NULL,
  landuse_level2 int references codelists.cl_landuse_type on update cascade on delete restrict NOT NULL,
  area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  au1 character varying(3) references admin_units.au_level1 on update cascade on delete restrict,
  au2 character varying(5) references admin_units.au_level2 on update cascade on delete restrict,
  au3 character varying(8) references admin_units.au_level3 on update cascade on delete restrict,
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_type_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_type_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_tbl TO reporting;

-- Index: data_landuse.idx_ca_landuse_type_landuse

-- DROP INDEX data_landuse.idx_ca_landuse_type_landuse;

CREATE INDEX idx_ca_landuse_type_landuse1
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (landuse);

-- Index: data_landuse.idx_ca_landuse_type_parcel_id

-- DROP INDEX data_landuse.idx_ca_landuse_type_parcel_id;

CREATE INDEX idx_ca_landuse_type_parcel_id1
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (parcel_id);

-- Index: data_landuse.idx_ca_landuse_type_valid_from

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_from;

CREATE INDEX idx_ca_landuse_type_valid_from1
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (valid_from);

-- Index: data_landuse.idx_ca_landuse_type_valid_till

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_till;

CREATE INDEX idx_ca_landuse_type_valid_till1
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (valid_till);

-- Index: data_landuse.st_idx_ca_landuse_type_tbl

-- DROP INDEX data_landuse.st_idx_ca_landuse_type_tbl;

CREATE INDEX st_idx_ca_landuse_type_tbl1
  ON data_landuse.ca_landuse_type_tbl
  USING gist
  (geometry);


-- Trigger: set_default_valid_time on data_landuse.ca_landuse_type_tbl

-- DROP TRIGGER set_default_valid_time ON data_landuse.ca_landuse_type_tbl;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

-- Trigger: update_area on data_landuse.ca_landuse_type_tbl

-- DROP TRIGGER update_area ON data_landuse.ca_landuse_type_tbl;

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

CREATE TRIGGER set_default_au3
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au3();

--------------

set search_path to data_landuse, public, codelists;
create or replace view ca_landuse_type as select * from ca_landuse_type_tbl 
WHERE ca_landuse_type_tbl.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_landuse_type_tbl.valid_from::timestamp with time zone, ca_landuse_type_tbl.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

grant select, insert, update, delete on ca_landuse_type to top_cadastre_update;
grant select on ca_landuse_type to top_cadastre_view, reporting;

