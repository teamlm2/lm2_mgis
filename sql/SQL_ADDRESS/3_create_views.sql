﻿CREATE OR REPLACE VIEW data_address.ca_parcel_address_view AS 
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

-----------

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