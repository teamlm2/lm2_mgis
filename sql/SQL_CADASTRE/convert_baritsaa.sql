DROP MATERIALIZED VIEW public.view_convert_lurs cascade;
CREATE MATERIALIZED VIEW public.view_convert_lurs AS 
select * from (
select bl."ID", date_part('year', bl.baritsaa_ehlesen_ognoo), row_number() over(partition by substring(date_part('year', bl.baritsaa_ehlesen_ognoo)::text, 3, 4)),
cpt.au2 || '-08-' || lpad(
(row_number() over(partition by substring(date_part('year', bl.baritsaa_ehlesen_ognoo)::text, 3, 4)) + coalesce((select max(split_part(ca.app_no, '-', 3)::int) from data_soums_union.ct_application ca 
where ca.app_type = 8 and ca.au2 = cpt.au2 and split_part(ca.app_no, '-', 4) = substring(date_part('year', bl.baritsaa_ehlesen_ognoo)::text, 3, 4)), 0))::text, 5, '0'
) || '-' || substring(date_part('year', bl.baritsaa_ehlesen_ognoo)::text, 3, 4) as new_app_no ,
bl.baritsaa_ehlesen_ognoo as app_timestamp, 
8 as app_type, cpt.landuse as approved_landuse, 
bl.duration_month, duration_month/12 as approved_duration, 
cpt.parcel_id, al.au1_code, cpt.au2, vcpda.app_no,
now() created_at, vcpda.rigth_type_code, 1 as status_id,  vcpda.contract_id,
(select bp.person_id from base.bs_person bp 
where bp.person_register = bl.register
order by bp.parent_id desc, bp.tin_id asc limit 1)
from public.baritsaa_lurs bl 
join data_soums_union.ca_parcel_tbl cpt on bl.old_pid::text = cpt.old_parcel_id 
join data_soums_union.view_ca_parcel_detail_active vcpda on cpt.parcel_id = vcpda.parcel_id
join admin_units.au_level2 al on cpt.au2 = al.code 
--where bl.parcel_id in ('1330100069', '1330200033')
group by cpt.parcel_id, cpt.au2, vcpda.app_no, bl."ID", cpt.landuse, al.au1_code, vcpda.rigth_type_code, vcpda.contract_id
order by substring(date_part('year', bl.baritsaa_ehlesen_ognoo)::text, 3, 4)
)sss where person_id is not null and new_app_no is not null;
ALTER TABLE public.view_convert_lurs
  OWNER TO geodb_admin;

----------
insert into data_soums_union.ct_application(app_no, app_timestamp, app_type, approved_landuse, approved_duration, parcel, au1, au2, created_at, updated_at, right_type, status_id)
select new_app_no, app_timestamp, app_type, approved_landuse, approved_duration, parcel_id, au1_code, au2, created_at, created_at, rigth_type_code, status_id from public.view_convert_lurs
where new_app_no is not null;
----------

DROP MATERIALIZED VIEW public.view_convert_lurs_app_person;
CREATE MATERIALIZED VIEW public.view_convert_lurs_app_person AS 
select app_no, app_id, person_id, 50 as role, false applicant, 0 as share from (
select * from (
select ca.app_no, ca.app_id,
(select bp.person_id from base.bs_person bp 
where bp.person_register = bl.registr
order by bp.parent_id desc, bp.tin_id asc limit 1),
(select bp.person_id from base.bs_person bp 
where bp.person_register = bl.register
order by bp.parent_id desc, bp.tin_id asc limit 1) as per_id
 from data_soums_union.ct_application ca 
join public.view_convert_lurs vcl on ca.app_no = vcl.new_app_no 
join public.baritsaa_lurs bl on vcl."ID" = bl."ID" 
where vcl.new_app_no is not null
)xxx where person_id is not null and per_id is not null
)xxx
union all
select app_no, app_id, per_id, 10 as role, true applicant, 1 as share from (
select * from (
select ca.app_no, ca.app_id,
(select bp.person_id from base.bs_person bp 
where bp.person_register = bl.registr
order by bp.parent_id desc, bp.tin_id asc limit 1),
(select bp.person_id from base.bs_person bp 
where bp.person_register = bl.register
order by bp.parent_id desc, bp.tin_id asc limit 1) as per_id
 from data_soums_union.ct_application ca 
join public.view_convert_lurs vcl on ca.app_no = vcl.new_app_no 
join public.baritsaa_lurs bl on vcl."ID" = bl."ID" 
where vcl.new_app_no is not null
)xxx where person_id is not null and per_id is not null
)xxx;
ALTER TABLE public.view_convert_lurs_app_person
  OWNER TO geodb_admin;
  
----------
insert into data_soums_union.ct_application_person_role (application, person, role, main_applicant, "share")
select vclap.app_id, vclap.person_id, vclap."role", vclap.applicant, vclap."share" from public.view_convert_lurs_app_person vclap 

----------

insert into data_soums_union.ct_application_status (application, status, status_date, officer_in_charge, next_officer_in_charge)
select vclap.app_id, 1, now(), 1048, 1048 from public.view_convert_lurs_app_person vclap 
group by vclap.app_id

--delete from data_soums_union.ct_application_status where application in (select vclap.app_id from public.view_convert_lurs_app_person vclap)

----------

insert into data_soums_union.ct_contract_application_role (application, contract, role)

select vclap.app_id, vcl.contract_id, 30 from public.view_convert_lurs_app_person vclap 
join public.view_convert_lurs vcl on vclap.app_no = vcl.new_app_no 
where vclap.role = 10 and vcl.contract_id is not null and vcl.rigth_type_code != 3

-------------

insert into data_soums_union.ct_app8_ext(start_mortgage_period, end_mortgage_period, mortgage_type, monetary_unit_type, monetary_unit_value, mortgage_status, app_id, created_by, created_at, person_id, loan_contract_no, mortgage_contract_no)

select bl.baritsaa_ehlesen_ognoo, 
case 
	when (date_part('year', bl.baritsaa_ehlesen_ognoo) + (round((bl.duration_month/12)::numeric, 0))::int ||'-'|| date_part('month', bl.baritsaa_ehlesen_ognoo) || '-' || date_part('day', bl.baritsaa_ehlesen_ognoo)) = '2031-2-29' then (date_part('year', bl.baritsaa_ehlesen_ognoo) + (round((bl.duration_month/12)::numeric, 0))::int ||'-'|| date_part('month', bl.baritsaa_ehlesen_ognoo) || '-' || date_part('day', bl.baritsaa_ehlesen_ognoo)-1)::Date
	else (date_part('year', bl.baritsaa_ehlesen_ognoo) + (round((bl.duration_month/12)::numeric, 0))::int ||'-'|| date_part('month', bl.baritsaa_ehlesen_ognoo) || '-' || date_part('day', bl.baritsaa_ehlesen_ognoo))::Date
end as duus_date,
10, 1, bl.amount, 
case 
	when bl.chuluulsun_ognoo is null then 10
	else 20
end as mortgage_status, vclap.app_id, 1048, now(), vclap.person_id, bl.mortgage_lend_no, bl.mortgage_contract_no 
from public.baritsaa_lurs bl 
join public.view_convert_lurs vcl on bl."ID" = vcl."ID" 
join public.view_convert_lurs_app_person vclap on vclap.app_no = vcl.new_app_no 
where vclap.role = 10
