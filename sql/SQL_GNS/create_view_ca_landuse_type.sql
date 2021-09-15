-- DROP VIEW data_landuse.ca_landuse_type;

CREATE OR REPLACE VIEW data_landuse.ca_landuse_type AS 
 SELECT ca_landuse_type_tbl.parcel_id,
    ca_landuse_type_tbl.is_active,
    ca_landuse_type_tbl.landuse,
    ca_landuse_type_tbl.landuse_level1,
    ca_landuse_type_tbl.landuse_level2,
    ca_landuse_type_tbl.area_m2,
    ca_landuse_type_tbl.address_khashaa,
    ca_landuse_type_tbl.address_streetname,
    ca_landuse_type_tbl.address_neighbourhood,
    ca_landuse_type_tbl.valid_from,
    ca_landuse_type_tbl.valid_till,
    ca_landuse_type_tbl.geometry,
    ca_landuse_type_tbl.au1,
    ca_landuse_type_tbl.au2,
    ca_landuse_type_tbl.au3,
    ca_landuse_type_tbl.created_by,
    ca_landuse_type_tbl.updated_by,
    ca_landuse_type_tbl.created_at,
    ca_landuse_type_tbl.updated_at,
    ca_landuse_type_tbl.cad_parcel_id
   FROM data_landuse.ca_landuse_type_tbl
  WHERE ca_landuse_type_tbl.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_landuse_type_tbl.valid_from::timestamp with time zone, ca_landuse_type_tbl.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_landuse.ca_landuse_type
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_type TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type TO top_cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type TO top_cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type TO cadastre_update;
