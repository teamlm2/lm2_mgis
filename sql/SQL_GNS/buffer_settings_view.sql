drop view if exists data_landuse.set_landuse_safety_zone;
CREATE OR REPLACE VIEW data_landuse.set_landuse_safety_zone AS 
select row_number() over() as id, * from (
select parcel_id::text, p.landuse, 
(st_buffer(geometry, (b.buffer_value * (select degrees_value from data_landuse.set_degrees_to_meters where id = 5)/(select meters_value from data_landuse.set_degrees_to_meters where id = 5)))) as geometry, 
p.au2, p.valid_from, p.valid_till 
from data_landuse.ca_landuse_type_tbl p, data_landuse.set_buffer_au2_landuse b
where p.landuse = b.landuse and p.au2 = b.au2 and parcel_id = 7325379 and is_active = true 
union all
select p.parcel_id, p.landuse, 
(st_buffer(geometry, (b.buffer_value * (select degrees_value from data_landuse.set_degrees_to_meters where id = 5)/(select meters_value from data_landuse.set_degrees_to_meters where id = 5)))) as geometry, 
p.au2, p.valid_from, p.valid_till
from data_landuse.set_buffer_parcel b, data_soums_union.ca_parcel_tbl p
where p.parcel_id = b.parcel_id
)p
where p.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true)) AND "overlaps"(p.valid_from::timestamp with time zone, p.valid_till::timestamp with time zone, (( SELECT set_role_user.pa_from
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone, (( SELECT set_role_user.pa_till
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))::timestamp with time zone);

ALTER TABLE data_landuse.set_landuse_safety_zone
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.set_landuse_safety_zone TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.set_landuse_safety_zone TO top_cadastre_update;
GRANT SELECT ON TABLE data_landuse.set_landuse_safety_zone TO top_cadastre_view;
GRANT SELECT ON TABLE data_landuse.set_landuse_safety_zone TO reporting;