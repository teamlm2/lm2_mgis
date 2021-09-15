set search_path to s06201, codelists, base, settings, admin_units, public;
create or replace view view_gt4_report as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.landuse,
	app_list.area_m2,area_ha,app_list.documented_area_m2,admin_unit1,admin_unit2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
	    app.app_timestamp,
	    parcel.parcel_id,
	    parcel.landuse,
	    parcel.area_m2,
	    parcel.area_m2 / 10000::numeric AS area_ha,
	    parcel.documented_area_m2,
	    au1.name AS admin_unit1,
	    au2.name AS admin_unit2,
	    parcel.address_khashaa,
	    parcel.address_streetname,
	    parcel.address_neighbourhood,
	    parcel.valid_from,
	    parcel.valid_till,
	    parcel.geometry,
	    row_number() over(partition by parcel.parcel_id) as rank
from ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and app.app_type != 6 and status.status = 9 and substring(parcel.landuse::text,1,1) = '6'
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt4_report to cadastre_update;
grant select on view_gt4_report to cadastre_view, reporting;