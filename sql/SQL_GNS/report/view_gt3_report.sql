----------
select 
au1.code as au1_code, au1.name as au1_name, at.code as app_type, at.description as app_type_name, all_value.parcel_area all_parcel_area, all_value.person_count all_person_count, round(sum(parcel.area_m2/10000), 2) as parcel_area, count(person.person_id) as person_count
from data_soums_union.ca_parcel_tbl parcel 
join data_soums_union.ct_application app on parcel.parcel_id = app.parcel
join codelists.cl_right_type rt on app.right_type = rt.code
join codelists.cl_application_type at on app.app_type = at.code
join data_soums_union.ct_application_person_role ap on app.app_id = ap.application
join base.bs_person person on ap.person = person.person_id
join admin_units.au_level1 au1 on app.au1 = au1.code
join (select 
au1.code as au1_code, au1.name as au1_name, round(sum(parcel.area_m2/10000), 2) as parcel_area, count(person.person_id) as person_count
from data_soums_union.ca_parcel_tbl parcel 
join data_soums_union.ct_application app on parcel.parcel_id = app.parcel
join codelists.cl_right_type rt on app.right_type = rt.code
join data_soums_union.ct_application_person_role ap on app.app_id = ap.application
join base.bs_person person on ap.person = person.person_id
join admin_units.au_level1 au1 on app.au1 = au1.code
where app.right_type = 3 and (person.type = 10 or person.type = 20) and au1 is not null and app.status_id != 8 and app.status_id > 6
group by au1.code, au1.name) all_value on app.au1 = all_value.au1_code
where app.right_type = 3 and (person.type = 10 or person.type = 20) and au1 is not null and app.status_id != 8 and app.status_id > 6
group by au1.code, au1.name, at.code, at.description, all_value.parcel_area, all_value.person_count
order by at.code
limit 25

------------

CREATE OR REPLACE VIEW data_soums_union.view_gt3_report AS 
 SELECT xxx.parcel_id,
    xxx.address_streetname,
    xxx.address_khashaa,
    xxx.landuse,
    xxx.right_type,
    xxx.area_ha,
    xxx.area_m2,
    xxx.valid_from,
    xxx.valid_till,
    xxx.geometry,
    xxx.au2
   FROM ( SELECT parcel.parcel_id,
            row_number() OVER (PARTITION BY parcel.parcel_id) AS rank,
            parcel.address_streetname,
            parcel.address_khashaa,
            landuse.description AS landuse,
            right_type.description AS right_type,
            parcel.area_m2 / 10000::numeric AS area_ha,
            parcel.area_m2,
            parcel.valid_from,
            parcel.valid_till,
            parcel.geometry,
            parcel.au2
           FROM data_soums_union.ca_parcel_tbl parcel
             JOIN data_soums_union.ct_application app ON parcel.parcel_id::text = app.parcel::text
             JOIN codelists.cl_right_type right_type ON app.right_type = right_type.code
             JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code) xxx
  WHERE xxx.rank = 1 AND xxx.au2::text = (( SELECT set_role_user.working_au_level2::text AS au2
           FROM settings.set_role_user
          WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true));

ALTER TABLE data_soums_union.view_gt3_report
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.view_gt3_report TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.view_gt3_report TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.view_gt3_report TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.view_gt3_report TO reporting;

