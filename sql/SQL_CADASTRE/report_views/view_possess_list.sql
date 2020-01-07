CREATE OR REPLACE VIEW data_soums_union.view_ownership_register_layer AS 

select  app.*, parcel.geometry from data_soums_union.ca_parcel_tbl parcel
join data_soums_union.view_ownership_register app on parcel.parcel_id = app.parcel_id
  WHERE parcel.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(parcel.valid_from::timestamp with time zone, parcel.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);


ALTER TABLE data_soums_union.view_ownership_register_layer
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.view_ownership_register_layer TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.view_ownership_register_layer TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.view_ownership_register_layer TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.view_ownership_register_layer TO reporting;

select * from (
select row_number() over(partition by app.parcel_id) as rank, app.parcel_id,app.*, parcel.geometry from data_soums_union.ca_parcel_tbl parcel
join data_soums_union.view_ownership_register app on parcel.parcel_id = app.parcel_id
  WHERE parcel.au2::text = '06201' --and parcel = '8213000314'
)xxx where rank > 1