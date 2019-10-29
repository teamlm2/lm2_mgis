insert into data_ub.ub_fee_history(person_register, pid, contract_no, document_area, zoriulalt, ner, payment_contract, payment_before_less, payment_before_over, payment_year, payment_fund, payment_loss, payment_total,
paid_year, paid_fund, paid_city, paid_district, invalid_payment, paid_less, paid_over, description, decision, current_year)

select person_register, pid, contract_no, document_area, zoriulalt, ner, payment_contract, payment_before_less, payment_before_over, payment_year, payment_fund, payment_loss, payment_total,
paid_year, paid_fund, paid_city, paid_district, invalid_payment, paid_less, paid_over, description, decision, current_year from data_ub.data_fee
where person_register is not null
