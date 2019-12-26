
-------------shalgah
select * from data_estimate.uvs_paid_2019
where contract_no not in
(
select contract_no from (
select row_number() over(partition by bayan.contract_no) as rank, bayan.* from data_estimate.pa_imposition im
join data_soums_union.ct_contract c on im.contract_id = c.contract_id
join data_soums_union.ct_fee fee on fee.id = im.fee_id
join base.bs_person person on fee.person = person.person_id
join data_estimate.uvs_paid_2019 bayan on im.parcel_id = bayan.parcel_id and upper(c.contract_no) = upper(bayan.contract_no) and upper(person.person_register) = upper(bayan.person_register)
where im.imposition_year = 2019
)xxx where rank = 1)


select * from data_estimate.uvs_paid_2019

--------------iluu dutuu tulultiin update hiih
with new_numbers as (
select bayan.remaining_amount, im.id from data_estimate.pa_imposition im
join data_soums_union.ct_contract c on im.contract_id = c.contract_id
join data_soums_union.ct_fee fee on fee.id = im.fee_id
join base.bs_person person on fee.person = person.person_id
join data_estimate.uvs_paid_2019 bayan on im.parcel_id = bayan.parcel_id and upper(c.contract_no) = upper(bayan.contract_no) and upper(person.person_register) = upper(bayan.person_register)
where im.imposition_year = 2019 and bayan.remaining_amount is not null
)
update data_estimate.pa_imposition set remainning_amount = nn.remaining_amount
from new_numbers nn
where data_estimate.pa_imposition.id = nn.id

-----------urd onii iluu dutuug tootsoh nogduulalt update hiih

update data_estimate.pa_imposition  set total_amount = year_amount - remainning_amount where remainning_amount != 0 and au2 = '06307' and imposition_year = 2019;


select year_amount, remainning_amount, year_amount - remainning_amount from data_estimate.pa_imposition
where au2 = '06307' and imposition_year = 2019

-----------------tulult hiih
insert into data_estimate.pa_payment_paid(fee_id, imposition_id, paid_year, remainning_amount, quarter_four, total_amount, year_amount, au2, parcel_id, contract_id, person_id, contract_amount, imposition_year_amount, imposition_total_amount, type_id)

select fee.id, im.id, 2019, abs(bayan.remaining_amount::numeric), bayan.paid_amount+bayan.remaining_amount::numeric, bayan.paid_amount, im.total_amount::numeric-bayan.paid_amount::numeric, '06307', bayan.parcel_id, c.contract_id, person.person_id, fee.fee_calculated, im.year_amount, im.total_amount, 1 from data_estimate.pa_imposition im
join data_soums_union.ct_contract c on im.contract_id = c.contract_id
join data_soums_union.ct_fee fee on fee.id = im.fee_id
join base.bs_person person on fee.person = person.person_id
join data_estimate.uvs_paid_2019 bayan on im.parcel_id = bayan.parcel_id and upper(c.contract_no) = upper(bayan.contract_no) and upper(person.person_register) = upper(bayan.person_register)
where im.imposition_year = 2019 and bayan.paid_amount is not null