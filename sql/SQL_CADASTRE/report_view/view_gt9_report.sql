set search_path to s06201, codelists, base, settings, admin_units, public;
create or replace view view_gt9_report as 
select 
    parcel_id,
    admin_unit1,
    admin_unit2,
    address_streetname,
    address_khashaa,
    record_right_type,
    landuse,
    person_type,
    person_id,
    name,
    first_name,
    approved_duration,
    area_ha,
    area_m2,
    valid_from,
    valid_till,
    geometry
from (
SELECT parcel.parcel_id,
    row_number() over(partition by parcel.parcel_id) as rank,
    au1.name AS admin_unit1,
    au2.name AS admin_unit2,
    parcel.address_streetname,
    parcel.address_khashaa,       
    record_right_type.description as record_right_type,
    landuse.description as landuse,
    person_type.description as person_type,
    person.person_id,
    person.name,
    person.first_name,
    app.approved_duration,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.valid_from,
    parcel.valid_till,
    parcel.geometry
FROM s06201.ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
join cl_person_type person_type on person.type = person_type.code
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
join ct_record_application_role record_app on app.app_no = record_app.application
join ct_ownership_record record on record_app.record = record.record_no
join cl_record_right_type record_right_type on record.right_type = record_right_type.code
)xxx where rank = 1 and record_right_type is not null and 
user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt9_report to cadastre_update;
grant select on view_gt9_report to cadastre_view, reporting;
