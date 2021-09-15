set search_path to s00000, codelists, base, settings, admin_units, public;
create or replace view view_land_tax_list as 

select app_list.name,app_list.first_name,app_list.person_id,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    app.app_timestamp,
	    parcel.parcel_id,
	    parcel.old_parcel_id,
	    parcel.geo_id,
	    parcel.landuse,
	    parcel.area_m2,
	    parcel.documented_area_m2,
	    parcel.address_khashaa,
	    parcel.address_streetname,
	    parcel.address_neighbourhood,
	    parcel.valid_from,
	    parcel.valid_till,
	    parcel.geometry,
	    row_number() over(partition by parcel.parcel_id) as rank
from ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_record_application_role record_app on app.app_no = record_app.application
inner join ct_ownership_record records on record_app.record = records.record_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join ct_tax_and_price tax on records.record_no = tax.record
inner join (select tax_payment.record, sum(tax_payment.amount_paid) amount_paid from ct_tax_and_price_payment tax_payment group by tax_payment.record) tax_payment on records.record_no = tax_payment.record
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9 and tax.land_tax > tax_payment.amount_paid
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_tax_list to cadastre_update;
grant select on view_land_tax_list to cadastre_view, reporting;