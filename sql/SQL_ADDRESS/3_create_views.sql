DROP VIEW if exists data_address.ca_parcel_address_view;

CREATE OR REPLACE VIEW data_address.ca_parcel_address_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_view TO cadastre_update;

----------
DROP VIEW if exists data_address.ca_parcel_address_is_new_view;
CREATE OR REPLACE VIEW data_address.ca_parcel_address_is_new_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE is_new_address = true and ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_is_new_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_is_new_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_is_new_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_is_new_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_is_new_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_is_new_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_is_new_view TO cadastre_update;

-----
DROP VIEW if exists data_address.ca_parcel_address_cadastre_view;
CREATE OR REPLACE VIEW data_address.ca_parcel_address_cadastre_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE parcel_type = 1 and ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_cadastre_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_cadastre_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_cadastre_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_cadastre_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_cadastre_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_cadastre_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_cadastre_view TO cadastre_update;

---------
DROP VIEW if exists data_address.ca_parcel_address_plan_view;
CREATE OR REPLACE VIEW data_address.ca_parcel_address_plan_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE parcel_type = 4 and ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_plan_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_plan_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_plan_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_plan_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_plan_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_plan_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_plan_view TO cadastre_update;

---------
DROP VIEW if exists data_address.ca_parcel_address_temp_cadastre_view;
CREATE OR REPLACE VIEW data_address.ca_parcel_address_temp_cadastre_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE parcel_type = 2 and ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_temp_cadastre_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_temp_cadastre_view TO cadastre_update;

---------
DROP VIEW if exists data_address.ca_parcel_address_bairzui_view;
CREATE OR REPLACE VIEW data_address.ca_parcel_address_bairzui_view AS 
 SELECT *
   FROM data_address.ca_parcel_address
  WHERE parcel_type = 7 and ca_parcel_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_address.valid_from::timestamp with time zone, ca_parcel_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_parcel_address_bairzui_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_parcel_address_bairzui_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_parcel_address_bairzui_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_parcel_address_bairzui_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_bairzui_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_parcel_address_bairzui_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address_bairzui_view TO cadastre_update;

-----------building

DROP VIEW data_address.ca_building_address_view;
CREATE OR REPLACE VIEW data_address.ca_building_address_view AS 
 SELECT *
   FROM data_address.ca_building_address
  WHERE ca_building_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_building_address.valid_from::timestamp with time zone, ca_building_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_building_address_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_building_address_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_building_address_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_building_address_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address_view TO cadastre_update;

--------
DROP VIEW if exists data_address.ca_building_address_is_new_view;
CREATE OR REPLACE VIEW data_address.ca_building_address_is_new_view AS 
 SELECT *
   FROM data_address.ca_building_address
  WHERE is_new_address = true and ca_building_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_building_address.valid_from::timestamp with time zone, ca_building_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_building_address_is_new_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_building_address_is_new_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_building_address_is_new_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_building_address_is_new_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_is_new_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_is_new_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address_is_new_view TO cadastre_update;
--------
DROP VIEW if exists data_address.ca_building_address_cadastre_view;
CREATE OR REPLACE VIEW data_address.ca_building_address_cadastre_view AS 
 SELECT *
   FROM data_address.ca_building_address
  WHERE parcel_type = 8 and ca_building_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_building_address.valid_from::timestamp with time zone, ca_building_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_building_address_cadastre_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_building_address_cadastre_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_building_address_cadastre_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_building_address_cadastre_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_cadastre_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_cadastre_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address_cadastre_view TO cadastre_update;

--------
DROP VIEW if exists data_address.ca_building_address_temp_cadastre_view;
CREATE OR REPLACE VIEW data_address.ca_building_address_temp_cadastre_view AS 
 SELECT *
   FROM data_address.ca_building_address
  WHERE parcel_type = 9 and ca_building_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_building_address.valid_from::timestamp with time zone, ca_building_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_building_address_temp_cadastre_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_building_address_temp_cadastre_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_building_address_temp_cadastre_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_building_address_temp_cadastre_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_temp_cadastre_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_temp_cadastre_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address_temp_cadastre_view TO cadastre_update;

--------
DROP VIEW if exists data_address.ca_building_address_bairzui_view;
CREATE OR REPLACE VIEW data_address.ca_building_address_bairzui_view AS 
 SELECT *
   FROM data_address.ca_building_address
  WHERE parcel_type = 10 and ca_building_address.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_building_address.valid_from::timestamp with time zone, ca_building_address.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.ca_building_address_bairzui_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.ca_building_address_bairzui_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.ca_building_address_bairzui_view TO reporting;
GRANT SELECT ON TABLE data_address.ca_building_address_bairzui_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_bairzui_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.ca_building_address_bairzui_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address_bairzui_view TO cadastre_update;
--------------
DROP VIEW if exists data_address.st_street_line_view;
CREATE OR REPLACE VIEW data_address.st_street_line_view AS 
select row_number() over() as fid, street_sub_id, street_name || '-' || street_code as street_name, ST_LineMerge(ST_Multi(St_Collect(line_geom))) from data_address.st_road
group by street_code, street_name, street_sub_id;
ALTER TABLE data_address.st_street_line_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_line_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_street_line_view TO reporting;
GRANT SELECT ON TABLE data_address.st_street_line_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_street_line_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_street_line_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_street_line_view TO cadastre_update;

-----------

