
drop table if exists codelists.cl_monetary_unit_type cascade;
create table codelists.cl_monetary_unit_type
(
code int primary key,
short_name varchar(75) unique not null,
description varchar(75)
);
grant select, insert, update, delete on codelists.cl_monetary_unit_type to land_office_administration;
grant select on codelists.cl_monetary_unit_type to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;
COMMENT ON TABLE codelists.cl_monetary_unit_type
  IS 'Мөнгөний нэгжийн төрөл';
  
insert into codelists.cl_monetary_unit_type values (1,'MNT','Төгрөг');
insert into codelists.cl_monetary_unit_type values (2,'USD','АНУ-ын доллар');
insert into codelists.cl_monetary_unit_type values (3,'CHY','БНХАУ-ын юань');
insert into codelists.cl_monetary_unit_type values (4,'RUB','ОХУ-ын рубль');
insert into codelists.cl_monetary_unit_type values (5,'JPY','Японы иен');
insert into codelists.cl_monetary_unit_type values (6,'GBR','Английн фунт');

insert into codelists.cl_monetary_unit_type values (7,'CHF','Швейцарийн франк');
insert into codelists.cl_monetary_unit_type values (8,'KRW','БНСУ-ын вон');
insert into codelists.cl_monetary_unit_type values (9,'HKD','Гонгконгийн доллар');
insert into codelists.cl_monetary_unit_type values (10,'AUD','Австралийн доллар');
insert into codelists.cl_monetary_unit_type values (11,'CAD','Канадын доллар');
insert into codelists.cl_monetary_unit_type values (12,'SGD','Сингапурын доллар');

alter table data_soums_union.ct_app8_ext add COLUMN person_id int REFERENCES base.bs_person on update cascade on delete cascade;

alter table data_soums_union.ct_app8_ext add COLUMN monetary_unit_type int REFERENCES codelists.cl_monetary_unit_type on update cascade on delete cascade;
alter table data_soums_union.ct_app8_ext add COLUMN monetary_unit_value NUMERIC;
alter table data_soums_union.ct_app8_ext add COLUMN mortgage_contract_no varchar(250);
alter table data_soums_union.ct_app8_ext add COLUMN loan_contract_no VARCHAR(250);

alter table data_soums_union.ct_app29_ext add COLUMN court_decision_no VARCHAR(250);

-----------------

with new_numbers as (
select app_person.person, app_person.application from data_soums_union.ct_application_person_role app_person
join data_soums_union.ct_app8_ext ex8 on app_person.application = ex8.app_id
join base.bs_person person on app_person.person = person.person_id
where app_person.role = 50
)
update data_soums_union.ct_app8_ext set person_id = nn.person
from new_numbers nn
where data_soums_union.ct_app8_ext.app_id = nn.application