CREATE OR REPLACE VIEW data_ub.ca_ub_parcel_fee AS 
 SELECT 
row_number() over() as gid,    
ca_ub_parcel_tbl.parcel_id,
    ca_ub_parcel_tbl.old_parcel_id,
    ca_ub_parcel_tbl.landuse,
    ca_ub_parcel_tbl.area_m2,
    h.document_area,
    h.current_year,
    h.city_type,
    ca_ub_parcel_tbl.address_khashaa,
    ca_ub_parcel_tbl.address_streetname,
    ca_ub_parcel_tbl.address_neighbourhood,
    ca_ub_parcel_tbl.valid_from,
    ca_ub_parcel_tbl.valid_till,
    ca_ub_parcel_tbl.geometry,
    ca_ub_parcel_tbl.edit_status,
    ca_ub_parcel_tbl.au2
   FROM data_ub.ca_ub_parcel_tbl
join data_ub.ub_fee_history h on ca_ub_parcel_tbl.old_parcel_id = h.pid
  WHERE ca_ub_parcel_tbl.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND (ca_ub_parcel_tbl.valid_till IS NULL OR ca_ub_parcel_tbl.valid_till = 'infinity'::date OR ca_ub_parcel_tbl.valid_till = '9999-12-31'::date);

ALTER TABLE data_ub.ca_ub_parcel_fee
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_ub.ca_ub_parcel_fee TO geodb_admin;
GRANT SELECT, INSERT ON TABLE data_ub.ca_ub_parcel_fee TO cadastre_update;
GRANT SELECT ON TABLE data_ub.ca_ub_parcel_fee TO reporting;
GRANT SELECT, UPDATE, INSERT ON TABLE data_ub.ca_ub_parcel_fee TO ub_parcel;
GRANT SELECT, INSERT ON TABLE data_ub.ca_ub_parcel_fee TO cadastre_view;
