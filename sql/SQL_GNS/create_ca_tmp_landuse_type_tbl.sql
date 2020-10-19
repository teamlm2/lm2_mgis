DROP TABLE if exists data_landuse.ca_landuse_maintenance_case cascade;

CREATE TABLE data_landuse.ca_landuse_maintenance_case
(
  id serial NOT NULL,
  creation_date date default now(),
  completion_date date,
  completed_by integer,
  landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
  workflow_id int references data_landuse.st_workflow on update cascade on delete restrict,
  status_id int references data_landuse.cl_landuse_movement_status on update cascade on delete restrict,
  created_by integer NOT NULL,
  created_at date,
  updated_by integer,  
  updated_at date,
  au2 character varying(5) NOT NULL,
  CONSTRAINT ca_landuse_maintenance_case_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_maintenance_case
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_maintenance_case TO geodb_admin;
GRANT SELECT, UPDATE, INSERT ON TABLE data_landuse.ca_landuse_maintenance_case TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_maintenance_case TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_maintenance_case TO cadastre_update;

GRANT ALL ON SEQUENCE data_landuse.ca_landuse_maintenance_case_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_case_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_case_id_seq TO application_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_case_id_seq TO cadastre_view;

--------------
DROP TABLE if exists data_landuse.ca_landuse_maintenance_status cascade;
CREATE TABLE data_landuse.ca_landuse_maintenance_status
(
  id serial PRIMARY KEY,
  case_id int references data_landuse.ca_landuse_maintenance_case on update cascade on delete restrict,
  status_id int references data_landuse.cl_landuse_movement_status on update cascade on delete restrict,
  status_date timestamp without time zone NOT NULL DEFAULT now(),
  officer_in_charge integer NOT NULL,
  next_officer_in_charge integer,
  description text
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_maintenance_status
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_maintenance_status TO geodb_admin;
GRANT SELECT ON TABLE data_landuse.ca_landuse_maintenance_status TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_maintenance_status TO application_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_maintenance_status TO application_view;

GRANT ALL ON SEQUENCE data_landuse.ca_landuse_maintenance_status_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_status_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_status_id_seq TO application_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_landuse_maintenance_status_id_seq TO cadastre_view;
---------------

CREATE OR REPLACE FUNCTION base.ca_landuse_maintenance_case_last_status_changes()
  RETURNS trigger AS
$BODY$
BEGIN        
        if (TG_OP = 'INSERT') THEN
                EXECUTE 'update data_landuse.ca_landuse_maintenance_case set status_id = ' || NEW.status || 'where id =' || NEW.case_id;
        ELSIF (TG_OP = 'DELETE') THEN
                EXECUTE 'update data_landuse.ca_landuse_maintenance_case set status_id = (select status_id from data_landuse.ca_landuse_maintenance_status
                                                                                        where case_id = '|| OLD.case_id ||'
                                                                                        group by case_id, status_id, id
                                                                                        order by id desc limit 1) where case_id =' || OLD.case_id;
        END IF;
        RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.ca_landuse_maintenance_case_last_status_changes()
  OWNER TO geodb_admin;

-- DROP TRIGGER app_last_status_change ON data_landuse.ca_landuse_maintenance_status;

CREATE TRIGGER app_last_status_change
  AFTER INSERT OR UPDATE OR DELETE
  ON data_landuse.ca_landuse_maintenance_status
  FOR EACH ROW
  EXECUTE PROCEDURE base.ca_landuse_maintenance_case_last_status_changes();

--------------

DROP TABLE if exists data_landuse.ca_landuse_parcel_maintenance_case cascade;

CREATE TABLE data_landuse.ca_landuse_parcel_maintenance_case
(
  case_id int references data_landuse.ca_landuse_maintenance_case on update cascade on delete restrict,
  landuse_parcel int references data_landuse.ca_landuse_type_tbl on update cascade on delete restrict,
  CONSTRAINT ca_landuse_parcel_maintenance_case_pkey PRIMARY KEY (landuse_parcel, case_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_parcel_maintenance_case
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_parcel_maintenance_case TO geodb_admin;
GRANT SELECT, UPDATE, INSERT ON TABLE data_landuse.ca_landuse_parcel_maintenance_case TO cadastre_view;
GRANT SELECT, INSERT ON TABLE data_landuse.ca_landuse_parcel_maintenance_case TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_parcel_maintenance_case TO cadastre_update;

-------------

DROP TABLE if exists data_landuse.ca_tmp_landuse_type_tbl cascade;
CREATE TABLE data_landuse.ca_tmp_landuse_type_tbl
(
  parcel_id serial PRIMARY KEY,
  is_active boolean not null DEFAULT false,
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
  au1 character varying(3) references admin_units.au_level1 on update cascade on delete restrict NOT NULL,
  au2 character varying(5) references admin_units.au_level2 on update cascade on delete restrict NOT NULL,
  au3 character varying(8) references admin_units.au_level3 on update cascade on delete restrict,
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  cad_parcel_id character varying(10) references data_soums_union.ca_parcel_tbl on update cascade on delete restrict,
  is_insert_cadastre boolean,
  case_id bigint references data_landuse.ca_landuse_maintenance_case on update cascade on delete restrict
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_tmp_landuse_type_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_tmp_landuse_type_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_tmp_landuse_type_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_tmp_landuse_type_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_tmp_landuse_type_tbl TO reporting;

GRANT ALL ON SEQUENCE data_landuse.ca_tmp_landuse_type_tbl_parcel_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_landuse.ca_tmp_landuse_type_tbl_parcel_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_tmp_landuse_type_tbl_parcel_id_seq TO application_update;
GRANT USAGE ON SEQUENCE data_landuse.ca_tmp_landuse_type_tbl_parcel_id_seq TO cadastre_view;
-- Index: data_landuse.idx_ca_landuse_type_landuse

-- DROP INDEX data_landuse.idx_ca_landuse_type_landuse;

CREATE INDEX idx_ca_tmp_landuse_type_landuse
  ON data_landuse.ca_tmp_landuse_type_tbl
  USING btree
  (landuse);

-- Index: data_landuse.idx_ca_landuse_type_parcel_id

-- DROP INDEX data_landuse.idx_ca_landuse_type_parcel_id;

CREATE INDEX idx_ca_tmp_landuse_type_parcel_id
  ON data_landuse.ca_tmp_landuse_type_tbl
  USING btree
  (parcel_id);

-- Index: data_landuse.idx_ca_landuse_type_valid_from

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_from;

CREATE INDEX idx_ca_tmp_landuse_type_valid_from
  ON data_landuse.ca_tmp_landuse_type_tbl
  USING btree
  (valid_from);

-- Index: data_landuse.idx_ca_landuse_type_valid_till

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_till;

CREATE INDEX idx_ca_tmp_landuse_type_valid_till
  ON data_landuse.ca_tmp_landuse_type_tbl
  USING btree
  (valid_till);

-- Index: data_landuse.st_idx_ca_tmp_landuse_type_tbl

-- DROP INDEX data_landuse.st_idx_ca_tmp_landuse_type_tbl;

CREATE INDEX st_idx_ca_tmp_landuse_type_tbl
  ON data_landuse.ca_tmp_landuse_type_tbl
  USING gist
  (geometry);


-- Trigger: set_default_valid_time on data_landuse.ca_tmp_landuse_type_tbl

-- DROP TRIGGER set_default_valid_time ON data_landuse.ca_tmp_landuse_type_tbl;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_tmp_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

-- Trigger: update_area on data_landuse.ca_tmp_landuse_type_tbl

-- DROP TRIGGER update_area ON data_landuse.ca_tmp_landuse_type_tbl;

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_tmp_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_tmp_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_tmp_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

CREATE TRIGGER set_default_au3
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_tmp_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au3();

-----------------------------

CREATE OR REPLACE VIEW data_landuse.ca_tmp_landuse_type AS 
 SELECT *
   FROM data_landuse.ca_tmp_landuse_type_tbl
  WHERE ca_tmp_landuse_type_tbl.is_active = true and ca_tmp_landuse_type_tbl.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_tmp_landuse_type_tbl.valid_from::timestamp with time zone, ca_tmp_landuse_type_tbl.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_landuse.ca_tmp_landuse_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_tmp_landuse_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_tmp_landuse_type TO top_cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_tmp_landuse_type TO top_cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_tmp_landuse_type TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_tmp_landuse_type TO cadastre_update;

----------------------------

DROP TABLE if exists data_landuse.st_movement_draft cascade;
CREATE TABLE data_landuse.st_movement_draft
(
  id serial PRIMARY KEY,
  start_date date NOT NULL,
  end_date date NOT NULL,
  decision_status integer,
  au2 character varying(5) DEFAULT NULL::character varying,
  decision_level int references codelists.cl_decision_level on update cascade on delete restrict,
  created_by integer,
  updated_by integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone NOT NULL DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_movement_draft
  OWNER TO geodb_admin;
  
GRANT ALL ON TABLE data_landuse.st_movement_draft TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_movement_draft TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.st_movement_draft TO application_view;

DROP TABLE if exists data_landuse.st_movement_draft_case cascade;
CREATE TABLE data_landuse.st_movement_draft_case
(
  case_id int references data_landuse.ca_landuse_maintenance_case on update cascade on delete restrict,
  decision_draft_id int references data_landuse.st_movement_draft on update cascade on delete restrict,
  CONSTRAINT st_movement_draft_case_pkey PRIMARY KEY (decision_draft_id, case_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_movement_draft_case
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.st_movement_draft_case TO geodb_admin;
GRANT SELECT, UPDATE, INSERT ON TABLE data_landuse.st_movement_draft_case TO cadastre_view;
GRANT SELECT, INSERT ON TABLE data_landuse.st_movement_draft_case TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_movement_draft_case TO cadastre_update;
