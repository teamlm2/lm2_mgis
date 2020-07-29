CREATE OR REPLACE VIEW data_address.st_street_start_point_view AS 

select row_number() over() as id, m.street_id, str.name::text || '-' || str.code::text as name, s.geometry from data_address.st_street_point s
join data_address.st_map_street_point m on s.id = m.street_point_id
join data_address.st_street str on m.street_id = str.id
--join data_address.st_street_line_view ss on st_intersects(s.geometry, ss.geometry)
join admin_units.au_level2 au2 on st_within(s.geometry, au2.geometry)

WHERE str.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(s.valid_from::timestamp with time zone, s.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.st_street_start_point_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_start_point_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_street_start_point_view TO reporting;
GRANT SELECT ON TABLE data_address.st_street_start_point_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_street_start_point_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_street_start_point_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_street_start_point_view TO cadastre_update;
