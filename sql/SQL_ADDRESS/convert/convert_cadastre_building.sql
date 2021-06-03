insert into data_address.ca_building_address(building_id, is_active, parcel_type, in_source, zipcode_id, street_id, address_building_no, address_parcel_no, au1, au2, created_at, valid_from, valid_till, geometry)

select xxx.building_id, case when xxx.valid_till::date <= now() then false else true end is_active, 8,  1, null, null, xxx.building_no, xxx.address_khashaa, substring(xxx.au2, 1, 3), xxx.au2, now(), xxx.valid_from, xxx.valid_till, xxx.geometry from data_soums_union.ca_building_tbl xxx
where xxx.au2 = '08110' and xxx.building_id not in (select building_id from data_address.ca_building_address b where b.au2 = '08110')

-------------cadastraas oruulsan negj talbaruudiid butsaaj parcel_type=8 bolgoh
with new_numbers as (
select aa.building_id, cba.id, cba.building_id as address_building_id, aa.building_no, aa.address_khashaa, aa.au2, aa.valid_from, aa.valid_till, aa.geometry from data_soums_union.ca_building_tbl aa 
join data_address.ca_building_address cba on aa.building_id = cba.building_id 
)
update data_address.ca_building_address
  set parcel_type = 8
from new_numbers s
where data_address.ca_building_address.id = s.id;

----------niisleliin barilgaas UPDATE hiih

select bb.geom, cba.geometry, (st_area(st_intersection(bb.geom, cba.geometry))/st_area(bb.geom)) as proportion
from data_address_cd.ub_building bb
join data_address.ca_building_address cba on st_intersects(bb.geom, cba.geometry)
where (st_area(st_intersection(bb.geom, cba.geometry))/st_area(bb.geom)) > 0.7
limit 100

----------niisleliin barilgaas INSERT hiih

select * from data_soums_union.ca_building_tbl
where au2 = '08110' and now() between '1900-01-01'::date and valid_till and building_id not in (
select aa.building_id from data_address.ca_building_address cba 
join data_soums_union.ca_building_tbl aa on st_equals(cba.geometry, aa.geometry)
where cba.au2 = '08110' and aa.au2 = '08110')