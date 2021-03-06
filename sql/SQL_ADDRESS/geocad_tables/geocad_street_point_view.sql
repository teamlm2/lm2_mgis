﻿DROP VIEW if exists data_address.geocad_street_point_view;

CREATE OR REPLACE VIEW data_address.geocad_street_point_view AS 
 SELECT *
   FROM data_address.all_street_point s
  WHERE st_intersects(( SELECT au_level2.geometry
           FROM admin_units.au_level2
          WHERE au_level2.code::text = (( SELECT set_role_user.working_au_level2::text AS au2
                   FROM settings.set_role_user
                  WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))), s.geometry);

ALTER TABLE data_address.geocad_street_point_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.geocad_street_point_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.geocad_street_point_view TO reporting;
GRANT SELECT ON TABLE data_address.geocad_street_point_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO cadastre_update;

