-- delete from data_ub.ub_fee_history

insert into data_ub.ub_fee_history(person_register, pid, contract_no, document_area, zoriulalt, ner, decision,
payment_contract, payment_before_less, payment_before_over, payment_year, payment_fund, payment_loss, payment_total, 
paid_before_less, paid_year, paid_fund, paid_city, paid_district, invalid_payment, paid_less, paid_over, description, current_year, city_type, au2)

select person_register, pid, contract_no, document_area::numeric, zoriulalt, ner, decision,
payment_contract::numeric, payment_before_less::numeric, payment_before_over::numeric, payment_year::numeric, payment_fund::numeric, payment_loss::numeric, payment_total::numeric, paid_before_less::numeric, paid_year::numeric, paid_fund::numeric, paid_city::numeric, paid_district::numeric, invalid_payment::numeric, paid_less::numeric, paid_over::numeric, description, current_year::int, 
2, '01110' from data_ub.fee_duureg_bayanzurkh