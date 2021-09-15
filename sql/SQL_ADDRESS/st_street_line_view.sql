DROP VIEW data_address.st_street_line_view;
CREATE OR REPLACE VIEW data_address.st_street_line_view AS

select row_number() over() as id, s.id as street_id, s.code, s.name, s.description, s.decision_date, s.decision_no, s.decision_level_id, dl.description as decision_level_desc, s.is_active, street_type_id, st.description as street_type_desc, s.length, r.geometry::geometry(LineString,4326) from data_address.st_street s
join data_address.cl_street_type st on s.street_type_id = st.code
left join data_plan.cl_plan_decision_level dl on s.decision_level_id = dl.plan_decision_level_id
join (select row_number() over() as gid, ((line_geom)) geometry, street_id from data_address.st_road
where street_id is not null ) r on s.id = r.street_id

WHERE s.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(s.valid_from::timestamp with time zone, s.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_address.st_street_line_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_street_line_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_street_line_view TO reporting;
GRANT SELECT ON TABLE data_address.st_street_line_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_street_line_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_street_line_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_street_line_view TO cadastre_update;