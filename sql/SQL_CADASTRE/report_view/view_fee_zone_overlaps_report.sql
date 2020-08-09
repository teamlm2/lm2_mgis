set search_path to s06201, codelists, base, settings, admin_units, public;
create or replace view view_fee_zone_overlaps_report as 
select parcel_id, address_streetname,address_khashaa,area_ha,area_m2,valid_from,valid_till,geometry from
(
SELECT parcel.parcel_id, 
    row_number() over(partition by parcel.parcel_id) as rank,
    parcel.address_streetname,
    parcel.address_khashaa,    
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.valid_from,
    parcel.valid_till,
    parcel.geometry
FROM s06201.ca_parcel_tbl parcel
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
join set_fee_zone fee_zone on st_overlaps(parcel.geometry, fee_zone.geometry)
)xxx where rank = 1
and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_fee_zone_overlaps_report to cadastre_update;
grant select on view_fee_zone_overlaps_report to cadastre_view, reporting;