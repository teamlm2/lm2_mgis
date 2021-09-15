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
drop table if exists codelists.cl_spa_mood;
CREATE TABLE codelists.cl_spa_mood
(
  code integer NOT NULL,
  description character varying(75) NOT NULL,
  short_name character varying(75) NOT NULL,
  description_en character varying(75),
  CONSTRAINT cl_spa_mood_pkey PRIMARY KEY (code),
  CONSTRAINT cl_spa_mood_description_en_key UNIQUE (description_en),
  CONSTRAINT cl_spa_mood_description_key UNIQUE (description)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_spa_mood
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_spa_mood TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_spa_mood TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_spa_mood TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_spa_mood TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_spa_mood TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_spa_mood TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_spa_mood TO reporting;
COMMENT ON TABLE codelists.cl_spa_mood
  IS 'Тусгай хэрэгцээний газрын төрөл';
  
insert into codelists.cl_spa_mood(code, description, short_name) values(1, 'Энгийн', 'Энгийн');
insert into codelists.cl_spa_mood(code, description, short_name) values(2, 'Нууц', 'Нууц');
insert into codelists.cl_spa_mood(code, description, short_name) values(3, 'Маш нууц', 'Маш нууц');

-----------------
set search_path to data_soums_union, codelists, public, base;

drop table if exists ca_spa_parcel_tbl;
create table ca_spa_parcel_tbl
(
id serial PRIMARY key,
parcel_id varchar(12) unique,
spa_land_name varchar(500),
area_m2 decimal,
spa_type int references codelists.cl_spa_type on update cascade on delete restrict,
spa_mood int references codelists.cl_spa_mood on update cascade on delete restrict,
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

alter table data_soums_union.ca_spa_parcel_tbl add column person_register varchar(10);

create or replace view data_soums_union.ca_spa_parcel as select * from data_soums_union.ca_spa_parcel_tbl p
where st_intersects(p.geometry, (select geometry from admin_units.au_level2 where code = (( SELECT set_role.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true))));

GRANT SELECT, INSERT ON TABLE data_soums_union.ca_spa_parcel TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.ca_spa_parcel TO reporting, application_view;

------------------
set search_path to data_soums_union, codelists, public, base;
drop table if exists ca_state_parcel_tbl;
create table ca_state_parcel_tbl
(
id serial PRIMARY key,
parcel_id varchar(12) unique,
land_name varchar(500),
address_neighbourhood character varying(250),
area_m2 decimal,
landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
spa_law varchar(250),
valid_from date default current_date,
valid_till date default 'infinity',
au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict,
department_id int references sdplatform.hr_department on update cascade on delete restrict,
geometry geometry(POLYGON, 4326)
);
grant select, insert, update, delete on ca_state_parcel_tbl to cadastre_update;
grant select on ca_state_parcel_tbl to cadastre_view, reporting;

CREATE INDEX st_idx_ca_state_parcel_tbl
  ON ca_state_parcel_tbl
  USING gist
  (geometry);

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON ca_state_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE update_area_or_length();

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON ca_state_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE set_default_valid_time();  

create or replace view data_soums_union.ca_state_parcel as select * from data_soums_union.ca_state_parcel_tbl p
where st_intersects(p.geometry, (select geometry from admin_units.au_level2 where code = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))));

GRANT SELECT, INSERT ON TABLE data_soums_union.ca_state_parcel TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.ca_state_parcel TO reporting, application_view;
-----------------

insert into codelists.cl_landuse_type(code, description) values(7101, 'Бичил уурхайн зориулалтаар олгосон газар');
insert into codelists.cl_landuse_type(code, description) values(7201, 'Хилийн боомтын бүс');
insert into codelists.cl_landuse_type(code, description) values(7301, 'Үндэсний хэмжээний томоохон бүтээн байгуулалт, дэд бүтцийн төсөл, хөтөлбөр хэрэгжүүлэх газар');
insert into codelists.cl_landuse_type(code, description) values(7401, 'Аюултай хог хаягдлын төвлөрсөн байгууламж барих газар');
----------------

insert into codelists.cl_application_type(code, description) values(31, '31: Тусгай хэрэгцээнд авах/гаргах');
insert into codelists.cl_application_type(code, description) values(32, '32: Төрийн өмчийн газрын бүртгэл');
insert into codelists.cl_application_type(code, description) values(33, '33: Газрын сангийн бүртгэл');

insert into codelists.cl_right_type(code, description, description_en) values (4, 'Төрийн өмч', 'State');
insert into settings.set_right_type_application_type(application_type, right_type) values (31, 4);
insert into settings.set_right_type_application_type(application_type, right_type) values (32, 4);
insert into settings.set_right_type_application_type(application_type, right_type) values (33, 4);

insert into settings.set_application_type_landuse_type(application_type, landuse_type)
select 33, code from codelists.cl_landuse_type;

insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6101);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6102);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6103);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6104);

insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6201);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6301);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6401);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6501);

insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6601);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6701);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6801);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 6901);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 7001);

------------

insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 7101);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 7201);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 7301);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(31, 7401);

-----------

insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(32, 2401);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(32, 2401);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(32, 7301);
insert into settings.set_application_type_landuse_type(application_type, landuse_type) values(32, 7401);

-------------

drop table if exists codelists.cl_parcel_type;
CREATE TABLE codelists.cl_parcel_type
(
  code integer PRIMARY KEY,
  description character varying(250),
  table_name character varying(250),
  python_model_name character varying(250),
  php_model_name character varying(250)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_parcel_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_parcel_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_parcel_type TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_parcel_type TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_parcel_type TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_parcel_type TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_parcel_type TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_parcel_type TO reporting;
COMMENT ON TABLE codelists.cl_parcel_type
  IS 'Нэгж талбарын төрөл';
  
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(1, 'Кадастрын үндсэн давхарга', 'data_soums_union.ca_parcel_tbl', 'CaParcelTbl');
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(2, 'Кадастрын ажлын давхарга', 'data_soums_union.ca_tmp_parcel', 'CaTmpParcel');
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(3, 'Бэлчээр/нөхөрлөлийн хил', 'data_soums_union.ca_pasture_parcel_tbl', 'CaPastureParcelTbl');
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(4, 'Газар зохион байгуулалтын төлөвлөгөө', 'data_plan.pl_project_parcel', 'PlProjectParcel');
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(5, 'Төрийн өмчийн газар', 'data_soums_union.ca_state_parcel_tbl', 'CaStateParcelTbl');
insert into codelists.cl_parcel_type(code, description, table_name, python_model_name) values(6, 'Тусгай хэрэгцээний газар', 'data_soums_union.ca_spa_parcel_tbl', 'CaSpaParcelTbl');

--------------

drop table if exists settings.set_application_type_parcel_type;
CREATE TABLE settings.set_application_type_parcel_type
(
  app_type int references codelists.cl_application_type on update cascade on delete restrict,
  parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict,
  PRIMARY KEY(app_type, parcel_type)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE settings.set_application_type_parcel_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE settings.set_application_type_parcel_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE settings.set_application_type_parcel_type TO land_office_administration;
GRANT SELECT ON TABLE settings.set_application_type_parcel_type TO cadastre_view;
GRANT SELECT ON TABLE settings.set_application_type_parcel_type TO cadastre_update;
GRANT SELECT ON TABLE settings.set_application_type_parcel_type TO contracting_view;
GRANT SELECT ON TABLE settings.set_application_type_parcel_type TO contracting_update;
GRANT SELECT ON TABLE settings.set_application_type_parcel_type TO reporting;
COMMENT ON TABLE settings.set_application_type_parcel_type
  IS 'Өргөдлийн төрөл болон Нэгж талбарын төрлийн тохиргоо';

insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (26, 3);
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (27, 3);
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (31, 6);
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (32, 5);
insert into settings.set_application_type_parcel_type (app_type, parcel_type) values (33, 5);
--------------------

drop table if exists data_soums_union.ct_application_parcel;
CREATE TABLE data_soums_union.ct_application_parcel
(
  app_id int references data_soums_union.ct_application on update cascade on delete restrict,
  parcel_id varchar(10),
  parcel_type int references codelists.cl_application_type on update cascade on delete restrict,
  PRIMARY KEY(app_id, parcel_id, parcel_type)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_soums_union.ct_application_parcel
  OWNER TO geodb_admin;
COMMENT ON TABLE data_soums_union.ct_application_parcel
IS 'Өргөдөл болон нэгж талбарын холбоос';
grant select, insert, update, delete on data_soums_union.ct_application_parcel to cadastre_update;
grant select on data_soums_union.ct_application_parcel to cadastre_view, reporting;

--------------------

drop table if exists sdplatform.hr_department_account;
CREATE TABLE sdplatform.hr_department_account
(
  department_id int references sdplatform.hr_department on update cascade on delete restrict,  
  bank_id int references codelists.cl_bank on update cascade on delete restrict,
  account_no character varying(50),
  PRIMARY KEY(department_id, bank_id, account_no)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE sdplatform.hr_department_account
  OWNER TO geodb_admin;
COMMENT ON TABLE sdplatform.hr_department_account
IS 'Хэлтэс болон дансны холбоос';
grant select, insert, update, delete on sdplatform.hr_department_account to cadastre_update;
grant select on sdplatform.hr_department_account to cadastre_view, reporting;

-------------------

alter table data_soums_union.ca_parcel_line_tbl add column valid_from date DEFAULT ('now'::text)::date;

alter table data_soums_union.ca_parcel_line_tbl add column valid_till date DEFAULT 'infinity'::date;


DROP VIEW if exists data_soums_union.ca_parcel_line;

CREATE OR REPLACE VIEW data_soums_union.ca_parcel_line AS 
 SELECT *
   FROM data_soums_union.ca_parcel_line_tbl
  WHERE  ca_parcel_line_tbl.au2::text = (( SELECT set_role.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true)) AND "overlaps"(ca_parcel_line_tbl.valid_from::timestamp with time zone, ca_parcel_line_tbl.valid_till::timestamp with time zone, (( SELECT set_role.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true))::timestamp with time zone, (( SELECT set_role.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true))::timestamp with time zone);

ALTER TABLE data_soums_union.ca_parcel_line
  OWNER TO geodb_admin;
GRANT SELECT, INSERT ON TABLE data_soums_union.ca_parcel_line TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.ca_parcel_line TO reporting;
GRANT SELECT ON TABLE data_soums_union.ca_parcel_line TO land_office_administration;
GRANT ALL ON TABLE data_soums_union.ca_parcel_line TO geodb_admin;
GRANT SELECT, INSERT, delete, update ON TABLE data_soums_union.ca_parcel_line TO cadastre_update;

---------------

DROP VIEW if exists data_soums_union.ca_sub_parcel;

CREATE OR REPLACE VIEW data_soums_union.ca_sub_parcel AS 
 SELECT *
   FROM data_soums_union.ca_sub_parcel_tbl
  WHERE  ca_sub_parcel_tbl.au2::text = (( SELECT set_role.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true)) AND "overlaps"(ca_sub_parcel_tbl.valid_from::timestamp with time zone, ca_sub_parcel_tbl.valid_till::timestamp with time zone, (( SELECT set_role.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true))::timestamp with time zone, (( SELECT set_role.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role.is_active = true))::timestamp with time zone);

ALTER TABLE data_soums_union.ca_sub_parcel
  OWNER TO geodb_admin;
GRANT SELECT, INSERT ON TABLE data_soums_union.ca_sub_parcel TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.ca_sub_parcel TO reporting;
GRANT SELECT ON TABLE data_soums_union.ca_sub_parcel TO land_office_administration;
GRANT ALL ON TABLE data_soums_union.ca_sub_parcel TO geodb_admin;
GRANT SELECT, INSERT, delete, update ON TABLE data_soums_union.ca_sub_parcel TO cadastre_update;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_soums_union.ca_parcel_line_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();
