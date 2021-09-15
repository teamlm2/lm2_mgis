CREATE TABLE data_estimate.pa_imposition_2020
(
  id serial,
  parcel_id varchar(10) REFERENCES data_soums_union.ca_parcel_tbl on update cascade on delete cascade,
  register_no varchar(10) NOT NULL,
  imposition_year integer NOT NULL,
  discount_percent numeric NOT NULL,
  discount_amount numeric NOT NULL,
  fee_calculated numeric,
  compensation_amount numeric,
  earning_amount numeric,
  remainning_amount numeric,
  year_amount numeric,
  total_amount numeric,
  quarter_one numeric,
  quarter_two numeric,
  quarter_three numeric,
  quarter_four integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_estimate.pa_imposition_2020
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_estimate.pa_imposition_2020 TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_estimate.pa_imposition_2020 TO land_office_administration;


insert into data_estimate.pa_imposition_2020(parcel_id, register_no, imposition_year, discount_percent, discount_amount, fee_calculated, compensation_amount, earning_amount, remainning_amount, year_amount, total_amount, quarter_one, quarter_two, quarter_three, quarter_four)

select ca_parcel_tbl.parcel_id, 
    bs_person.person_register, 
    pa_imposition.imposition_year,
    ct_fee.subsidized_fee_rate,
    pa_imposition.discount_amount,
    ct_fee.fee_calculated,
    pa_imposition.compensation_amount,
    pa_imposition.earning_amount,
    pa_imposition.remainning_amount,
    pa_imposition.year_amount,
    pa_imposition.total_amount,
    pa_imposition.quarter_one,
    pa_imposition.quarter_two,
    pa_imposition.quarter_three,
    pa_imposition.quarter_four from data_estimate.pa_imposition pa_imposition
join data_soums_union.ct_fee ct_fee on pa_imposition.fee_id = ct_fee.id
join base.bs_person bs_person on ct_fee.person = bs_person.person_id
join data_soums_union.ct_contract ct_contract on ct_fee.contract = ct_contract.contract_id and ct_contract.status = 20
join data_soums_union.ct_contract_application_role ct_contract_application_role on ct_contract_application_role.contract = ct_contract.contract_id and ct_contract_application_role.role = 20
join data_soums_union.ct_application ct_application on ct_contract_application_role.application = ct_application.app_id
join data_soums_union.ca_parcel_tbl ca_parcel_tbl on ca_parcel_tbl.parcel_id = ct_application.parcel
where pa_imposition.au2 = '06307' and pa_imposition.imposition_year = 2020