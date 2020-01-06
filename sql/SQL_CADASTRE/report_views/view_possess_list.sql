CREATE OR REPLACE VIEW data_soums_union.view_land_possessors_list1 AS 
select parcel.parcel_id, parcel.old_parcel_id, parcel.area_m2, parcel.address_streetname, parcel.address_khashaa, parcel.address_neighbourhood, parcel.valid_from, parcel.valid_till, app.app_no, app.app_timestamp, parcel.property_no, app.app_type, app.status_id, parcel.geometry from data_soums_union.ca_parcel_tbl parcel
join data_soums_union.ct_application app on parcel.parcel_id = app.parcel
  WHERE app.right_type = 2 AND parcel.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(parcel.valid_from::timestamp with time zone, parcel.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);
ALTER TABLE data_soums_union.view_land_possessors_list1
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.view_land_possessors_list1 TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.view_land_possessors_list1 TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.view_land_possessors_list1 TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.view_land_possessors_list1 TO reporting;

select * from (
select row_number() over(partition by parcel.parcel_id) as rank, parcel.parcel_id, parcel.old_parcel_id, parcel.area_m2, parcel.address_streetname, parcel.address_khashaa, parcel.address_neighbourhood, parcel.valid_from, parcel.valid_till, app.app_no, app.app_timestamp, parcel.property_no, app.app_type, app.status_id, parcel.geometry from data_soums_union.ca_parcel_tbl parcel
join data_soums_union.ct_application app on parcel.parcel_id = app.parcel
where parcel.au2 = '06201' --and parcel = '8213000314'
)xxx where rank > 1