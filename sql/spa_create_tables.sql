set search_path to data_soums_union, codelists, public;
CREATE TABLE codelists.cl_spa_type
(
  code integer NOT NULL,
  description character varying(75) NOT NULL,
  short_name character varying(75) NOT NULL,
  description_en character varying(75),
  CONSTRAINT cl_spa_type_pkey PRIMARY KEY (code),
  CONSTRAINT cl_spa_type_description_en_key UNIQUE (description_en),
  CONSTRAINT cl_spa_type_description_key UNIQUE (description)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_spa_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_spa_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_spa_type TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_spa_type TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_spa_type TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_spa_type TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_spa_type TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_spa_type TO reporting;
COMMENT ON TABLE codelists.cl_spa_type
  IS 'Тусгай хэрэгцээний газрын төрөл';
  
insert into codelists.cl_spa_type(code, description, short_name) values(1, 'Улсын тусгай хэрэгцээ', 'УТХ');
insert into codelists.cl_spa_type(code, description, short_name) values(2, 'Орон нутгийн тусгай хэрэгцээ', 'ОНТХ');

--------------------

CREATE TABLE codelists.cl_spa_status
(
  code integer NOT NULL,
  description character varying(75) NOT NULL,
  short_name character varying(75) NOT NULL,
  description_en character varying(75),
  CONSTRAINT cl_spa_status_pkey PRIMARY KEY (code),
  CONSTRAINT cl_spa_status_description_en_key UNIQUE (description_en),
  CONSTRAINT cl_spa_status_description_key UNIQUE (description)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_spa_status
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_spa_status TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_spa_status TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_spa_status TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_spa_status TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_spa_status TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_spa_status TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_spa_status TO reporting;
COMMENT ON TABLE codelists.cl_spa_status
  IS 'Тусгай хэрэгцээний газрын төрөл';
  
insert into codelists.cl_spa_status(code, description, short_name) values(1, 'Энгийн', 'Энгийн');
insert into codelists.cl_spa_status(code, description, short_name) values(2, 'Нууц', 'Нууц');
insert into codelists.cl_spa_status(code, description, short_name) values(3, 'Маш нууц', 'Маш нууц');

-----------------
set search_path to data_soums_union, codelists, public, base;

create table ca_spa_parcel_tbl
(
id serial PRIMARY key,
parcel_id varchar(12) unique,
spa_land_name varchar(500),
area_m2 decimal,
spa_type int references codelists.cl_spa_type on update cascade on delete restrict,
landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
spa_law varchar(250),
decision_level int references data_plan.cl_plan_decision_level on update cascade on delete restrict,
decision_date date,
decision_no varchar(20),
contract_date date,
contract_no varchar(20),
certificate_date date,
certificate_no varchar(20),
valid_from date default current_date,
valid_till date default 'infinity',
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
department_id int references sdplatform.hr_department on update cascade on delete restrict,
geometry geometry(POLYGON, 4326)
);
grant select, insert, update, delete on ca_spa_parcel_tbl to cadastre_update;
grant select on ca_spa_parcel_tbl to cadastre_view, reporting;

CREATE INDEX st_idx_ca_spa_parcel_tbl
  ON ca_spa_parcel_tbl
  USING gist
  (geometry);

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON ca_spa_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE update_area_or_length();

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON ca_spa_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE set_default_valid_time();  