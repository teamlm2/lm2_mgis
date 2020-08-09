--application_list
set search_path to s00000, codelists, base, settings, admin_units, public;
create or replace view view_application_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and (status.status = 1 or status.status = 2 or status.status = 3 or status.status = 4)
order by app.app_timestamp asc
)app_list where rank = 1 
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_application_list to cadastre_update;
grant select on view_application_list to cadastre_view, reporting;

--end_of_this_year


create or replace view view_end_of_this_year_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where status.status = 9 and app_person.main_applicant = true and parcel.valid_till = 'infinity' and contract.contract_end > now() and (contract.contract_end::timestamp with time zone - now()) < '1 year'::interval
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_end_of_this_year_list to cadastre_update;
grant select on view_end_of_this_year_list to cadastre_view, reporting;

--governor_decision_list


create or replace view view_governor_decision_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 7
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_governor_decision_list to cadastre_update;
grant select on view_governor_decision_list to cadastre_view, reporting;

-- land_fee_list


create or replace view view_land_fee_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join ct_fee fee on contract.contract_no = fee.contract
inner join (select fee_payment.contract, sum(fee_payment.amount_paid) amount_paid from ct_fee_payment fee_payment group by fee_payment.contract) fee_payment on contract.contract_no = fee_payment.contract
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9 and fee.fee_calculated > fee_payment.amount_paid
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_fee_list to cadastre_update;
grant select on view_land_fee_list to cadastre_view, reporting;

--landfee_payment_list


create or replace view view_land_fee_payment_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join ct_fee fee on contract.contract_no = fee.contract
inner join (select fee_payment.contract, sum(fee_payment.amount_paid) amount_paid from ct_fee_payment fee_payment group by fee_payment.contract) fee_payment on contract.contract_no = fee_payment.contract
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9 and fee.fee_calculated <= fee_payment.amount_paid
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_fee_payment_list to cadastre_update;
grant select on view_land_fee_payment_list to cadastre_view, reporting;

---land_ownership_list


create or replace view view_land_ownerships_list as 
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
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_ownerships_list to cadastre_update;
grant select on view_land_ownerships_list to cadastre_view, reporting;

---land_possessors_list


create or replace view view_land_possessors_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and app.app_type != 6 and status.status = 9
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_possessors_list to cadastre_update;
grant select on view_land_possessors_list to cadastre_view, reporting;

---landtax_list


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

--land_tax_payment_list


create or replace view view_land_tax_payment_list as 

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
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9 and tax.land_tax <= tax_payment.amount_paid
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_tax_payment_list to cadastre_update;
grant select on view_land_tax_payment_list to cadastre_view, reporting;

-- land_users_list


create or replace view view_land_users_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and app.app_type = 6 and status.status = 9
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_land_users_list to cadastre_update;
grant select on view_land_users_list to cadastre_view, reporting;

--land_refused_list


create or replace view view_refused_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 8
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_refused_list to cadastre_update;
grant select on view_refused_list to cadastre_view, reporting;


--waiting_list

create or replace view view_waiting_list as 
select app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.old_parcel_id,app_list.geo_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
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
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and (status.status = 5 or status.status = 6)
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_waiting_list to cadastre_update;
grant select on view_waiting_list to cadastre_view, reporting;

--gt1

create or replace view view_gt1_report as 
SELECT parcel.parcel_id,
    au1.name AS admin_unit1,
    au2.name AS admin_unit2,   
    parcel.address_streetname,
    parcel.address_khashaa,    
    substring(landuse.code::text, 1, 1)::integer AS lcode1,
    case 
	when substring(landuse.code::text, 1, 1)::integer = 1 then 'Хөдөө аж ахуйн газар газар'
	when substring(landuse.code::text, 1, 1)::integer = 2 then 'Хот, тосгон, бусад суурины газар'
	when substring(landuse.code::text, 1, 1)::integer = 3 then 'Зам шугам сүлжээний газар'
	when substring(landuse.code::text, 1, 1)::integer = 4 then 'Ойн сан бүхий газар'
	when substring(landuse.code::text, 1, 1)::integer = 5 then 'Усны сан бүхий газар'
	when substring(landuse.code::text, 1, 1)::integer = 6 then 'Улсын тусгай хэрэгцээний газар'
	else 'Хоосон'
    end as lcode1_desc,
    landuse.code2 AS lcode2,
    landuse.description2 as lcode2_desc,
    landuse.code AS lcode3,
    landuse.description as lcode3_desc,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.geometry
FROM s00000.ca_parcel_tbl parcel
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
where user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt1_report to cadastre_update;
grant select on view_gt1_report to cadastre_view, reporting;

--gt2_3

create or replace view view_gt2_report as 
select 
    parcel_id,
    admin_unit1,
    admin_unit2,
    address_streetname,
    address_khashaa,       
    landuse,
    person_type,
    right_type,
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
    landuse.description as landuse,
    person_type.description as person_type,
    right_type.description as right_type,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.valid_from,
    parcel.valid_till,
    parcel.geometry
FROM s00000.ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
join cl_person_type person_type on person.type = person_type.code
join set_right_type_application_type app_right_type on app.app_type = app_right_type.application_type
join cl_right_type right_type on app_right_type.right_type = right_type.code
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
)xxx where rank = 1 and
user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt2_report to cadastre_update;
grant select on view_gt2_report to cadastre_view, reporting;

--gt4

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

--gt6

create or replace view view_gt6_report as 
select 
    parcel_id,
    admin_unit1,
    admin_unit2,
    address_streetname,
    address_khashaa,
    pollution_type,
    pollution_code,
    landuse,
    person_type,
    person_id,
    name,
    first_name,
    approved_duration,
    decision_date,
    right_type,
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
    pollution_type.description as pollution_type,
    pollution_type.code as pollution_code,
    landuse.description as landuse,
    person_type.description as person_type,
    person.person_id,
    person.name,
    person.first_name,
    app.approved_duration,
    decision.decision_date,
    right_type.description as right_type,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.valid_from,
    parcel.valid_till,
    parcel.geometry
FROM s00000.ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
join cl_person_type person_type on person.type = person_type.code
join set_right_type_application_type app_right_type on app.app_type = app_right_type.application_type
join cl_right_type right_type on app_right_type.right_type = right_type.code
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
join ct_decision_application decision_app on app.app_no = decision_app.application
join ct_decision decision on decision_app.decision = decision.decision_no
join ca_parcel_pollution_tbl pollution on st_contains(pollution.geometry,parcel.geometry)
join cl_pollution_type pollution_type on pollution.pollution = pollution_type.code
)xxx where rank = 1 and pollution_type is not null and
user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt6_report to cadastre_update;
grant select on view_gt6_report to cadastre_view, reporting;

--gt7

create or replace view view_gt7_report as 
select 
    parcel_id,
    admin_unit1,
    admin_unit2,
    address_streetname,
    address_khashaa,
    conservation_type,
    conservation_code,
    landuse,
    person_type,
    person_id,
    name,
    first_name,
    approved_duration,
    decision_date,
    right_type,
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
    conservation_type.description as conservation_type,
    conservation_type.code as conservation_code,
    landuse.description as landuse,
    person_type.description as person_type,
    person.person_id,
    person.name,
    person.first_name,
    app.approved_duration,
    decision.decision_date,
    right_type.description as right_type,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.valid_from,
    parcel.valid_till,
    parcel.geometry
FROM s00000.ca_parcel_tbl parcel
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
join cl_person_type person_type on person.type = person_type.code
join set_right_type_application_type app_right_type on app.app_type = app_right_type.application_type
join cl_right_type right_type on app_right_type.right_type = right_type.code
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
join ct_decision_application decision_app on app.app_no = decision_app.application
join ct_decision decision on decision_app.decision = decision.decision_no
join ca_parcel_conservation_tbl conservation on ST_within(parcel.geometry,conservation.geometry)
join cl_conservation_type conservation_type on conservation.conservation = conservation_type.code
)xxx where rank = 1 and conservation_type is not null and
user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt7_report to cadastre_update;
grant select on view_gt7_report to cadastre_view, reporting;

--gt8

create or replace view view_gt8_report as 
select app_list.admin_unit1,app_list.admin_unit2,app_list.name,app_list.first_name,app_list.person_id,app_list.status,app_list.app_timestamp,app_list.parcel_id,app_list.landuse,
	app_list.area_m2,app_list.documented_area_m2,app_list.address_khashaa,
	app_list.address_streetname,app_list.address_neighbourhood,app_list.valid_from,app_list.valid_till,app_list.geometry from 
(
select 		
	    au1.name AS admin_unit1,
	    au2.name AS admin_unit2,
	    person.name,
	    person.first_name,
	    person.person_id,
	    status.status,
	    app.app_timestamp,
	    parcel.parcel_id,
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
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
inner join ct_application app on parcel.parcel_id = app.parcel
inner join ct_contract_application_role contract_app on app.app_no = contract_app.application
inner join ct_contract contract on contract_app.contract = contract.contract_no
inner join ct_application_person_role app_person on app.app_no = app_person.application
inner join bs_person person on app_person.person = person.id
inner join ct_fee fee on contract.contract_no = fee.contract
inner join (select fee_payment.contract, sum(fee_payment.amount_paid) amount_paid from ct_fee_payment fee_payment group by fee_payment.contract) fee_payment on contract.contract_no = fee_payment.contract
inner join (select application,max(status) as status from ct_application_status group by application order by application) status on app.app_no = status.application
where app_person.main_applicant = true and parcel.valid_till = 'infinity' and status.status = 9 and fee.fee_calculated <= fee_payment.amount_paid
order by app.app_timestamp asc
)app_list where rank = 1
	and user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt8_report to cadastre_update;
grant select on view_gt8_report to cadastre_view, reporting;

--gt9
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
FROM s00000.ca_parcel_tbl parcel
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
