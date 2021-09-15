insert into data_ub.ub_fee_history(person_register, pid, contract_no, document_area, zoriulalt, ner, payment_contract, payment_before_less, payment_before_over, payment_year, payment_fund, payment_loss, payment_total,
paid_year, paid_fund, paid_city, paid_district, invalid_payment, paid_less, paid_over, description, decision, current_year, city_type, au2)

select person_register, pid, contract_no, document_area, zoriulalt, ner, payment_contract, payment_before_less, payment_before_over, payment_year, payment_fund, payment_loss, payment_total,
paid_year, paid_fund, case when paid_city ~ '^([0-9]+[.]?[0-9]*|[.][0-9]+)$' then paid_city::numeric else 0 end as paid_city, paid_district, invalid_payment, paid_less, paid_over, description, decision, current_year, city_type, '01113' from data_ub.fee_duureg_nalaikh
--where person_register is not null
