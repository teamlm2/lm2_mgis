CREATE OR REPLACE VIEW data_cama.ca_parcel_mass_price AS 

 SELECT 
row_number() over() as gid,
ca_parcel_tbl.parcel_id,
    ca_parcel_tbl.old_parcel_id,
    mp.calculate_year,
mp.mass_price,
mp.mass_price_m2,
mp.in_active,
    ca_parcel_tbl.landuse,
    ca_parcel_tbl.area_m2,
    ca_parcel_tbl.address_khashaa,
    ca_parcel_tbl.address_streetname,
    ca_parcel_tbl.address_neighbourhood,
    ca_parcel_tbl.valid_from,
    ca_parcel_tbl.valid_till,
    ca_parcel_tbl.geometry,
    ca_parcel_tbl.au2
   FROM data_soums_union.ca_parcel_tbl
join data_cama.cm_parcel_mass_price mp on data_soums_union.ca_parcel_tbl.parcel_id = mp.parcel_id
  WHERE (ca_parcel_tbl.org_type IN ( SELECT o.role_org_id
           FROM settings.set_role_organization o
             JOIN settings.set_role_user r ON o.organization_id = r.organization AND r.user_name::name = "current_user"() AND r.is_active = true)) AND ca_parcel_tbl.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(ca_parcel_tbl.valid_from::timestamp with time zone, ca_parcel_tbl.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_cama.ca_parcel_mass_price
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_cama.ca_parcel_mass_price TO geodb_admin;
GRANT SELECT ON TABLE data_cama.ca_parcel_mass_price TO reporting;
GRANT SELECT ON TABLE data_cama.ca_parcel_mass_price TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_cama.ca_parcel_mass_price TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_cama.ca_parcel_mass_price TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_cama.ca_parcel_mass_price TO cadastre_update;