insert into codelists.cl_application_type(code, description) values(33, '33: Газрын сангийн бүртгэл');
insert into settings.set_right_type_application_type(application_type, right_type) values (33, 4);

insert into settings.set_application_type_landuse_type(application_type, landuse_type)
select 33, code from codelists.cl_landuse_type;
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (33, 2);
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (33, 1);

drop table if exists codelists.cl_state_parcel_type;
CREATE TABLE codelists.cl_state_parcel_type
(
  code integer NOT NULL,
  description character varying(75) NOT NULL,
  description_en character varying(75),
  CONSTRAINT cl_state_parcel_type_pkey PRIMARY KEY (code),
  CONSTRAINT cl_state_parcel_type_description_en_key UNIQUE (description_en),
  CONSTRAINT cl_state_parcel_type_description_key UNIQUE (description)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_state_parcel_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_state_parcel_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_state_parcel_type TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_state_parcel_type TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_state_parcel_type TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_state_parcel_type TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_state_parcel_type TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_state_parcel_type TO reporting;
COMMENT ON TABLE codelists.cl_state_parcel_type
  IS 'Төрийн өмчийн газрын төрөл';
  
insert into codelists.cl_state_parcel_type(code, description) values(1, 'Газрын санд бүртгэсэн');
insert into codelists.cl_state_parcel_type(code, description) values(2, 'Төрийн өмчийн газарт бүртгэсэн');

ALTER TABLE data_soums_union.ca_state_parcel_tbl ADD COLUMN state_parcel_type INT REFERENCES codelists.cl_state_parcel_type ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE ONLY data_soums_union.ca_state_parcel_tbl ALTER COLUMN state_parcel_type SET DEFAULT 2;

ALTER TABLE data_soums_union.ct_application_parcel ALTER COLUMN parcel_id TYPE varchar (15);

DROP VIEW data_soums_union.ca_state_parcel;
ALTER TABLE data_soums_union.ca_state_parcel_tbl ALTER COLUMN parcel_id TYPE varchar (15);
create or replace view data_soums_union.ca_state_parcel as select * from data_soums_union.ca_state_parcel_tbl p
where st_intersects(p.geometry, (select geometry from admin_units.au_level2 where code = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))));

GRANT SELECT, INSERT ON TABLE data_soums_union.ca_state_parcel TO cadastre_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.ca_state_parcel TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.ca_state_parcel TO reporting, application_view;

GRANT ALL ON SEQUENCE data_soums_union.ca_state_parcel_tbl_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_soums_union.ca_state_parcel_tbl_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_soums_union.ca_state_parcel_tbl_id_seq TO application_update;

ALTER TABLE codelists.cl_parcel_type ADD COLUMN is_insert_state_parcel BOOLEAN;

UPDATE codelists.cl_parcel_type set is_insert_state_parcel = TRUE WHERE code = 1;
UPDATE codelists.cl_parcel_type set is_insert_state_parcel = TRUE WHERE code = 2;