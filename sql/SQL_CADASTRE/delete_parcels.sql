
delete from data_soums_union.ct_application
where parcel in
(select parcel_id::text from public.delete_parcels_048
where type = 1);

delete from data_plan.pl_project_parcel_ref_parcel
where cad_parcel_id in
(select parcel_id::text from public.delete_parcels_048
where type = 1);

delete from data_soums_union.ca_parcel_tbl
where parcel_id in
(select parcel_id::text from public.delete_parcels_048
where type = 1);

-----------------

delete from data_soums_union.ct_record_application_role
where record in
(select app_r.record from public.delete_parcels_048 d
join data_soums_union.ct_application app on d.parcel_id::text = app.parcel
join data_soums_union.ct_record_application_role app_r on app.app_id = app_r.application
where type = 2);

delete from data_soums_union.ct_ownership_record
where record_id in
(select app_r.record from public.delete_parcels_048 d
join data_soums_union.ct_application app on d.parcel_id::text = app.parcel
join data_soums_union.ct_record_application_role app_r on app.app_id = app_r.application
where type = 2);

-----------------

delete from data_soums_union.ct_contract_application_role
where contract in
(select app_r.contract from public.delete_parcels_048 d
join data_soums_union.ct_application app on d.parcel_id::text = app.parcel
join data_soums_union.ct_contract_application_role app_r on app.app_id = app_r.application
where type = 3);

delete from data_soums_union.ct_contract
where contract_id in
(select app_r.contract from public.delete_parcels_048 d
join data_soums_union.ct_application app on d.parcel_id::text = app.parcel
join data_soums_union.ct_contract_application_role app_r on app.app_id = app_r.application
where type = 3);

------test
delete from data_soums_union.ct_ownership_record
where record_id in
(
select record_id from (
select app_r.record, r.record_id, r.record_no, r.au2  from data_soums_union.ct_ownership_record r
left join data_soums_union.ct_record_application_role app_r on r.record_id = app_r.record
)xxx where record is null and substring(au2, 1, 3) = '048')

delete from data_soums_union.ct_contract_fee
where contract_id in
(
select contract_id from (
select app_r.contract, r.contract_id, r.contract_no, r.au2, app_id  from data_soums_union.ct_contract r
left join data_soums_union.ct_contract_application_role app_r on r.contract_id = app_r.contract
left join data_soums_union.ct_application app on app_r.application = app.app_id
--where r.contract_no = '4831-2004/00211'
)xxx where app_id is null and substring(au2, 1, 3) = '048')

delete from data_soums_union.ct_contract_detail
where contract_id in
(
select contract_id from (
select app_r.contract, r.contract_id, r.contract_no, r.au2, app_id  from data_soums_union.ct_contract r
left join data_soums_union.ct_contract_application_role app_r on r.contract_id = app_r.contract
left join data_soums_union.ct_application app on app_r.application = app.app_id
--where r.contract_no = '4831-2004/00211'
)xxx where app_id is null and substring(au2, 1, 3) = '048')

delete from data_soums_union.ct_contract_application_role
where contract in
(
select contract_id from (
select app_r.contract, r.contract_id, r.contract_no, r.au2, app_id  from data_soums_union.ct_contract r
left join data_soums_union.ct_contract_application_role app_r on r.contract_id = app_r.contract
left join data_soums_union.ct_application app on app_r.application = app.app_id
--where r.contract_no = '4831-2004/00211'
)xxx where app_id is null and substring(au2, 1, 3) = '048')

delete from data_soums_union.ct_contract
where contract_id in
(
select contract_id from (
select app_r.contract, r.contract_id, r.contract_no, r.au2, app_id  from data_soums_union.ct_contract r
left join data_soums_union.ct_contract_application_role app_r on r.contract_id = app_r.contract
left join data_soums_union.ct_application app on app_r.application = app.app_id
--where r.contract_no = '4831-2004/00211'
)xxx where app_id is null and substring(au2, 1, 3) = '048')


select contract_id from (
select app_r.contract, r.contract_id, r.contract_no, r.au2, app_id  from data_soums_union.ct_contract r
left join data_soums_union.ct_contract_application_role app_r on r.contract_id = app_r.contract
left join data_soums_union.ct_application app on app_r.application = app.app_id
--where r.contract_no = '4831-2004/00211'
)xxx where app_id is null and substring(au2, 1, 3) = '048'

select app_r.record from public.delete_parcels_048 d
join data_soums_union.ct_application app on d.parcel_id::text = app.parcel
join data_soums_union.ct_record_application_role app_r on app.app_id = app_r.application
where type = 2