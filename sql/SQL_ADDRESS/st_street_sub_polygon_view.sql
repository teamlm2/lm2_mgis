CREATE OR REPLACE VIEW data_address.st_street_sub_polygon_view AS 
 select * from data_address.st_street s
  WHERE s.parent_id is not null and s.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(s.valid_from::timestamp with time zone, s.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.st_street_sub_polygon_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_sub_polygon_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_street_sub_polygon_view TO reporting;
GRANT SELECT ON TABLE data_address.st_street_sub_polygon_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_street_sub_polygon_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_street_sub_polygon_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_street_sub_polygon_view TO cadastre_update;
