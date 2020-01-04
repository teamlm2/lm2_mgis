select * from (
select contract.contract_no as contract, row_number() over(partition by contract.contract_no) as rank ,paid.* from data_estimate.uvs_paid_2019 paid
join data_soums_union.ca_parcel_tbl parcel on paid.parcel_id = parcel.parcel_id
join base.bs_person person on paid.person_register = person.person_register
join data_soums_union.ct_application app on paid.parcel_id = app.parcel
join data_soums_union.ct_application_person_role app_person on app.app_id = app_person.application
join data_soums_union.ct_contract_application_role contract_app on app.app_id = contract_app.application
join data_soums_union.ct_contract contract on contract_app.contract = contract.contract_id

where contract.status = 20 and contract_app.role = 20
)xxx where rank = 1

-----

with new_numbers as (
select * from (
select contract.contract_no as contract, row_number() over(partition by contract.contract_no) as rank ,paid.* 
from data_estimate.uvs_paid_2019 paid
join data_soums_union.ca_parcel_tbl parcel on paid.parcel_id = parcel.parcel_id
join base.bs_person person on paid.person_register = person.person_register
join data_soums_union.ct_application app on paid.parcel_id = app.parcel
join data_soums_union.ct_application_person_role app_person on app.app_id = app_person.application and person.person_id = app_person.person
join data_soums_union.ct_contract_application_role contract_app on app.app_id = contract_app.application and contract_app.role = 20
join data_soums_union.ct_contract contract on contract_app.contract = contract.contract_id and contract.status = 20

where paid.contract_no is null
order by contract.created_at desc
)xxx where rank = 1
)
update data_estimate.uvs_paid_2019 set contract_no = nn.contract
from new_numbers nn
where data_estimate.uvs_paid_2019.id = nn.id and data_estimate.uvs_paid_2019.contract_no is null


----------

select * from data_estimate.uvs_paid_2019 paid
where contract_no is null


update data_estimate.uvs_paid_2019 set remaining_amount = null where remaining_amount = '-'


