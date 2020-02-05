
delete from data_soums_union.ct_application
where parcel = '';

delete from data_plan.pl_project_parcel_ref_parcel
where cad_parcel_id = '';

delete from data_soums_union.ca_parcel_tbl
where parcel_id = '';

-----------------

delete from data_soums_union.ct_record_application_role
where record in
(select app_r.record from data_soums_union.ct_application app
join data_soums_union.ct_record_application_role app_r on app.app_id = app_r.application
where app.parcel = '');

delete from data_soums_union.ct_ownership_record
where record_id in
(select app_r.record from data_soums_union.ct_application app
join data_soums_union.ct_record_application_role app_r on app.app_id = app_r.application
where app.parcel = '');

-----------------

delete from data_soums_union.ct_contract_application_role
where contract in
(select app_r.contract from data_soums_union.ct_application app
join data_soums_union.ct_contract_application_role app_r on app.app_id = app_r.application
where app.parcel = '');

delete from data_soums_union.ct_contract
where contract_id in
(select app_r.contract from data_soums_union.ct_application app
join data_soums_union.ct_contract_application_role app_r on app.app_id = app_r.application
where app.parcel = '');

