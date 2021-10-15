with new_numbers as (
select cppt.parcel_id, cppt.au2, al.code from data_soums_union.ca_pasture_parcel_tbl cppt 
join admin_units.au_level2 al on st_within(ST_PointOnSurface(cppt.geometry), al.geometry)
where st_isvalid(cppt.geometry) is true
)
update data_soums_union.ca_pasture_parcel_tbl
  set au2 = s.code
from new_numbers s
where data_soums_union.ca_pasture_parcel_tbl.parcel_id = s.parcel_id;

-----------

select  
(select coalesce(max(substring(cpg.group_no::text, 5, 3)::int), 0) from data_soums_union.ct_person_group cpg 
where substring(cpg.group_no::text, 1, 4)::int = code::int and substring(cpg.group_no::text, 1, 4) ~ '^-?[0-9]+\.?[0-9]*$' and substring(cpg.group_no::text, 5, 3) ~ '^-?[0-9]+\.?[0-9]*$'),
row_number() over(partition by code) as n_no,
(code::int)::text || ((select coalesce(max(substring(cpg.group_no::text, 5, 3)::int), 0) from data_soums_union.ct_person_group cpg 
where substring(cpg.group_no::text, 1, 4)::int = code::int and substring(cpg.group_no::text, 1, 4) ~ '^-?[0-9]+\.?[0-9]*$' and substring(cpg.group_no::text, 5, 3) ~ '^-?[0-9]+\.?[0-9]*$') + row_number() over(partition by code))::text,
*
from (
select row_number() over(partition by bp.person_register) as rank,  bp.person_register, al.code, mu.geom from public.malchin_urkh mu 
join base.bs_person bp on upper(split_part(mu.person_reg, ',', 1)) = upper(bp.person_register)   
join admin_units.au_level2 al on st_within(st_centroid(mu.geom), al.geometry)
where mu.person_reg is not null and mu.geom is not null
group by bp.person_register, mu.geom, al.code
order by al.code
)sss where rank = 1

-----------malchdiin bulgiin burtel
--DROP MATERIALIZED VIEW public.view_malchid_buleg;
CREATE MATERIALIZED VIEW public.view_malchid_buleg AS 
select au2.code || ((select max(split_part(cpb.code, au2.code, 2)::int) from data_soums_union.ca_pug_boundary cpb 
where cpb.au2 = au2.code) + row_number() over(partition by au2.code))::text as boundary_code,  row_number() over(partition by au2.code) num,
(au2.code::int)::text || ((select max(split_part(cpb.group_no::text, (au2.code::int)::text, 2)::int) from data_soums_union.ct_person_group cpb 
where cpb.au2 = au2.code and (split_part(cpb.group_no::text, (au2.code::int)::text, 2)) ~ '^-?[0-9]+\.?[0-9]*$') + row_number() over(partition by au2.code))::text as group_no,
4 as group_type, 
aa.register, bb.person_id, bb.person_register, aa.ahlagch, split_part(aa.ahlagch, '.', 1) ovog, split_part(aa.ahlagch, '.', 2) ner, 
aa.hg_name, aa.geom, au2.code as au2, au1.code as au1, au3.code as au3 from public.heseg_bnd aa
left join base.bs_person bb on upper(aa.register) = upper(bb.person_register)
join admin_units.au_level3 au3 on st_within(st_centroid(aa.geom), au3.geometry)
join admin_units.au_level2 au2 on st_within(st_centroid(aa.geom), au2.geometry)
join admin_units.au_level1 au1 on au2.au1_code = au1.code 
WITH DATA;
ALTER TABLE public.view_malchid_buleg
  OWNER TO geodb_admin;
-----------

insert into data_soums_union.ca_pug_boundary(code, group_name, geometry, au2, group_type)
select aa.boundary_code, aa.hg_name, aa.geom, aa.au2, aa.group_type from public.view_malchid_buleg aa

-----------

insert into data_soums_union.ct_person_group(group_no, group_name, is_contract, created_date, au2, boundary_code, group_type, citizen_count, au1, au3)
select aa.group_no::int, aa.hg_name, 'No Contract' is_contract, now(), aa.au2, aa.boundary_code, aa.group_type, 1, aa.au1 , aa.au3 from public.view_malchid_buleg aa

-----------

insert into data_soums_union.ct_group_member(group_no, person, "role", person_register)
select aa.group_no::int, aa.person_id, 10, aa.person_register from public.view_malchid_buleg aa
where aa.person_id is not null

-----------malchin urkhiin burtel

--DROP MATERIALIZED VIEW public.view_malchid_urkh;
CREATE MATERIALIZED VIEW public.view_malchid_urkh AS 

select * from (
select row_number() over(partition by gid) as rank, * from (
select 
(cpt.au2::int)::text || (select max(split_part(cpb.group_no::text, (cpt.au2::int)::text, 2)::int) from data_soums_union.ct_person_group cpb 
where cpb.au2 = cpt.au2 and split_part(cpb.group_no::text, (cpt.au2::int)::text, 2) ~ '^-?[0-9]+\.?[0-9]*$') + row_number() over(partition by cpt.au2) as group_no,
imu.gid, imu.land_name, imu.owner_name, imu.pasture_ty, ca.app_timestamp, bp.person_id, bp.person_register, bp.first_name, satpr.is_owner, cpt.parcel_id, cpt.landuse, imu.geom, al.au1_code au1, cpt.au2, au3.code as au3 from public.insure_malchin_urkh imu 
join data_soums_union.ca_parcel_tbl cpt on st_within(imu.geom, cpt.geometry)
left join admin_units.au_level3 au3 on st_within(imu.geom, au3.geometry)
join admin_units.au_level2 al on cpt.au2 = al.code 
join data_soums_union.ct_application ca on cpt.parcel_id = ca.parcel 
join data_soums_union.ct_application_person_role capr on ca.app_id = capr.application 
join base.bs_person bp on capr.person = bp.person_id 
join settings.set_application_type_person_role satpr on ca.app_type = satpr."type" and capr."role" = satpr."role" 
where satpr.is_owner is true  --and cpt.au2 = '06419' --and cpt.parcel_id = '6425000433' 
order by cpt.au2, cpt.parcel_id, ca.app_timestamp desc
)xxx)ggg where rank = 1

WITH DATA;

ALTER TABLE public.view_malchid_urkh
  OWNER TO geodb_admin;

-----------

insert into data_soums_union.ct_person_group(group_no, group_name, is_contract, created_date, au2, boundary_code, group_type, citizen_count, au1, au3)
select aa.group_no::int, aa.land_name, 'No Contract', now(), aa.au2, null, 3, 1, aa.au1, aa.au3 from public.view_malchid_urkh aa 

-----------

insert into data_soums_union.ct_group_member(group_no, person, "role", person_register)
select aa.group_no::int, aa.person_id, 10, aa.person_register from public.view_malchid_urkh aa 

-----------

insert into pasture.ps_person_group_location (person_group, pasture_type, current_year, geometry, created_by, created_at, au1, au2, au3)
select aa.group_no::integer, aa.pasture_ty::int, 2021, aa.geom, 999, now(), aa.au1, au2, aa.au3 from public.view_malchid_urkh aa

----------------
with new_numbers as (
select id, current_year, pasture_type, cpt.description, 
case 
	when pasture_type = 17 then (current_year::text ||'-'||'05' || '-20')::Date
	when pasture_type = 18 then (current_year::text ||'-'||'09' || '-15')::Date
	when pasture_type = 19 then (current_year::text ||'-'||'11' || '-01')::Date
	when pasture_type = 20 then (current_year::text ||'-'||'04' || '-01')::Date
	when pasture_type = 21 then (current_year::text ||'-'||'11' || '-01')::Date
	when pasture_type = 22 then (current_year::text ||'-'||'05' || '-20')::Date
	when pasture_type = 23 then (current_year::text ||'-'||'04' || '-01')::Date
	when pasture_type = 24 then (current_year::text ||'-'||'09' || '-15')::Date
	else null
end as start_date,
case 
	when pasture_type = 17 then (current_year::text ||'-'||'09' || '-15')::Date
	when pasture_type = 18 then (current_year::text ||'-'||'11' || '-01')::Date
	when pasture_type = 19 then (current_year::text ||'-'||'04' || '-01')::Date
	when pasture_type = 20 then (current_year::text ||'-'||'05' || '-20')::Date
	when pasture_type = 21 then (current_year::text ||'-'||'05' || '-20')::Date
	when pasture_type = 22 then (current_year::text ||'-'||'09' || '-15')::Date
	when pasture_type = 23 then (current_year::text ||'-'||'09' || '-15')::Date
	when pasture_type = 24 then (current_year::text ||'-'||'04' || '-01')::Date
	else null
end as end_date
from pasture.ps_person_group_location aa
join codelists.cl_pasture_type cpt on aa.pasture_type = cpt.code 
)
update pasture.ps_person_group_location
  set start_date = s.start_date, end_date = s.end_date
from new_numbers s
where pasture.ps_person_group_location.id = s.id;



-----------
select (select max(split_part(cpb.code, au2.code, 2)::int) from data_soums_union.ca_pug_boundary cpb 
where cpb.au2 = au2.code) + row_number() over(partition by au2.code) as boundary_code,  row_number() over(partition by au2.code) num,
4 as group_type, 
aa.register, bb.person_register, aa.ahlagch, split_part(aa.ahlagch, '.', 1) ovog, split_part(aa.ahlagch, '.', 2) ner, 
aa.hg_name, aa.geom, au2.code as au2, au1.code as au1, au3.code as au3 from public.heseg_bnd aa
left join base.bs_person bb on upper(aa.register) = upper(bb.person_register)
join admin_units.au_level3 au3 on st_within(st_centroid(aa.geom), au3.geometry)
join admin_units.au_level2 au2 on st_within(st_centroid(aa.geom), au2.geometry)
join admin_units.au_level1 au1 on au2.au1_code = au1.code 


select max(split_part(cpb.group_no::text, ('06419'::int)::text, 2)::int) from data_soums_union.ct_person_group cpb 
where cpb.au2 = '06419'
group by cpb.group_no
order by cpb.group_no

select * from data_soums_union.ct_person_group
where group_no = 640437

