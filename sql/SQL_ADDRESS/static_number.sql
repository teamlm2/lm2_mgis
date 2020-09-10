select count(pp.parcel_id) from data_plan.pl_project p
join data_plan.cl_plan_type pt on p.plan_type_id = pt.plan_type_id
join data_plan.pl_project_parcel pp on p.project_id = pp.project_id
where pt.code in ('04', '05', '07', '12') and p.is_active = true and now() between '1900-01-01'::date and p.end_date
--order by p.start_date desc

-------------

select count(*) from data_address.ca_parcel_address
where valid_till > now()

select count(*) from data_address.ca_building_address
where valid_till > now()

select * from data_address.ca_parcel_address
where valid_till < now()
order by valid_till asc

--------------

select count(pp.parcel_id) from data_plan.pl_project p
join data_plan.cl_plan_type pt on p.plan_type_id = pt.plan_type_id
join data_plan.pl_project_parcel pp on p.project_id = pp.project_id
where pt.code in ('04', '05', '07', '12') and p.is_active = true and now() between p.start_date and p.end_date
--order by p.start_date desc

------------
select address_khashaa, address_streetname, split_part(address_streetname, '-', 2), SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, '-', 2))) from data_soums_union.ca_parcel_tbl
where char_length(address_khashaa) > 2 and 
SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, '-', 2))) = split_part(address_streetname, '-', 2) and SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, '-', 2))) != ''
--limit 1000

-------------

select address_khashaa, address_streetname, split_part(address_streetname, ' ', 2), SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) from data_soums_union.ca_parcel_tbl
where char_length(address_khashaa) > 2 and 
SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) = split_part(address_streetname, ' ', 2) and SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) != ''
--limit 1000


--------------

with new_numbers as (
select parcel_id, address_khashaa, address_streetname, split_part(address_streetname, ' ', 2), SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) from data_soums_union.ca_parcel_tbl
where char_length(address_khashaa) > 2 and 
SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) = split_part(address_streetname, ' ', 2) and SUBSTRING(address_khashaa, 1, char_length(split_part(address_streetname, ' ', 2))) != ''
)
update data_address.ca_parcel_address
  set is_new_address = true
from new_numbers s
where data_address.ca_parcel_address.parcel_id = s.parcel_id;

-----
select count(id) from data_address.ca_parcel_address
where is_new_address = true

-------


delete from data_address.ca_parcel_address where parcel_type = 4;
insert into data_address.ca_parcel_address(parcel_id, is_active, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, status, parcel_type, geometry, valid_from, valid_till)

select parcel_id, false, gazner, gazner, pp.au1, pp.au2, pp.au3, 4, 1, 4, polygon_geom, valid_from, valid_till from data_plan.pl_project p
join data_plan.cl_plan_type pt on p.plan_type_id = pt.plan_type_id
join data_plan.pl_project_parcel pp on p.project_id = pp.project_id
where pt.code in ('04', '05', '07', '12') and p.is_active = true and now() between p.start_date and p.end_date and workrule_status_id = 15


----------

select count(p.parcel_id) from data_soums_union.ca_parcel_tbl p,
(select parcel_id, false, gazner, gazner, pp.au1, pp.au2, pp.au3, 4, 1, 4, polygon_geom, valid_from, valid_till from data_plan.pl_project p
join data_plan.cl_plan_type pt on p.plan_type_id = pt.plan_type_id
join data_plan.pl_project_parcel pp on p.project_id = pp.project_id
where pt.code in ('04', '05', '07', '12') and p.is_active = true and now() between p.start_date and p.end_date and workrule_status_id = 15) x
where st_equals(p.geometry, x.polygon_geom) and st_isvalid(p.geometry) = true and st_isvalid(x.polygon_geom) = true


----------------------
select * from data_soums_union.ct_application app
join data_soums_union.ca_tmp_plan_parcel p on app.app_id = p.app_id
where project_parcel is not null

------

select bz.address_parcel_no, bz.address_streetname, bz.street_code, p.address_parcel_no, p.address_streetname, p.street_code from (select * from data_address.ca_parcel_address
where parcel_type = 7 and au2 = '04201') as bz, (select * from data_address.ca_parcel_address
where parcel_type = 1 and au2 = '04201' and is_new_address = true and now() between '1900-01-01'::date and valid_till) p
where st_within(st_centroid(bz.geometry), p.geometry) and bz.address_streetname || '-' || bz.street_code = p.address_streetname and bz.address_parcel_no = p.address_parcel_no