CREATE OR REPLACE VIEW data_address.au2_settlement_zone_view AS 
select * from admin_units.au_settlement_zone_view s
WHERE st_intersects(( SELECT au_level2.geometry
           FROM admin_units.au_level2
          WHERE au_level2.code::text = (( SELECT set_role_user.working_au_level2::text AS au2
                   FROM settings.set_role_user
                  WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))), s.geometry);

ALTER TABLE data_address.au2_settlement_zone_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.au2_settlement_zone_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.au2_settlement_zone_view TO reporting;
GRANT SELECT ON TABLE data_address.au2_settlement_zone_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.au2_settlement_zone_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.au2_settlement_zone_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.au2_settlement_zone_view TO cadastre_update;
