insert into data_address.ca_building_address(building_id, is_active, parcel_type, in_source, zipcode_id, street_id, address_building_no, address_parcel_no, au1, au2, created_at, valid_from, valid_till, geometry)
select xxx.building_id, case when xxx.valid_till::date <= now() then false else true end is_active, 8,  1, null, null, xxx.building_no, xxx.address_khashaa, substring(xxx.au2, 1, 3), xxx.au2, now(), xxx.valid_from, xxx.valid_till, xxx.geometry from (
select cbt.*, cba.building_id add_b_id, cba.id from data_soums_union.ca_building_tbl cbt
left join data_address.ca_building_address cba on cbt.building_id = cba.building_id 
)xxx where add_b_id is null

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

select cba.id, bb.geom, cba.geometry, (st_area(st_intersection(bb.geom, cba.geometry))/st_area(bb.geom)) as proportion
from data_address_cd.ub_building bb
join data_address.ca_building_address cba on st_intersects(bb.geom, cba.geometry)
where bb.address_building_id is null and (st_area(st_intersection(bb.geom, cba.geometry))/st_area(bb.geom)) > 0.7
limit 100

----------niisleliin barilgaas INSERT hiih

insert into data_address.ca_building_address(building_id, is_active, parcel_type, in_source, zipcode_id, street_id, building_name, address_building_no, address_parcel_no, au1, au2, created_at, valid_from, valid_till, geometry)
select ub.gid, true, 14, 10, null, null, bldng_name, bldng_numb, bldng_numb, substring(al.code , 1, 3) as au1, al.code as au2, now(), now(), null, ub.geom from data_address_cd.ub_building ub 
join admin_units.au_level2 al on st_intersects(ub.geom, al.geometry)
where al.code = '01107' and ub.gid not in (select ub.gid from data_address_cd.ub_building ub 
left join data_address.ca_building_address cba on st_overlaps(ub.geom, cba.geometry) or st_covers(ub.geom, cba.geometry)
where cba.au2 = '01107') --and ub.gid = 2380

----------niisleliin barilgatai 70% dawhardaj baigaa bailgiin id-g ub_building-tai holboh
with new_number as (
select bb.gid, cba.id, bb.geom, cba.geometry, (st_area(st_intersection(bb.geom, cba.geometry))/st_area(bb.geom)) as proportion
from data_address_cd.ub_building bb
join data_address.ca_building_address cba on st_intersects(bb.geom, cba.geometry)
where bb.address_building_id is null and (st_area(st_intersection((bb.geom), (cba.geometry)))/st_area(bb.geom)) > 0.7
--and st_isvalid(bb.geom) is false and st_isvalid(cba.geometry) is false 
)
update data_address_cd.ub_building set address_building_id = s.id
from new_number s 
where data_address_cd.ub_building.gid = s.gid

---test
select * from data_address_cd.ub_building ub where address_building_id is not null

select count(*) from data_address_cd.ub_building where st_isvalid(geom) is false
update data_address_cd.ub_building set geom = (st_dump(ST_CollectionExtract(ST_MakeValid(geom),3))).geom where st_isvalid(geom) is false

select count(*) from data_address.ca_building_address where st_isvalid(geometry) is false
update data_address.ca_building_address set geometry = (st_dump(ST_CollectionExtract(ST_MakeValid(geometry),3))).geom where st_isvalid(geometry) is false