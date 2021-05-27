insert into data_address.ca_building_address_history(building_id, is_active, in_source, zipcode_id, street_id, address_building_no, address_parcel_no au1, au2, created_at, valid_from, valid_till, geometry)

select xxx.building_id, true, 1, null, null, xxx.building_no, xxx.address_khashaa, substring(xxx.au2, 1, 3), xxx.au2, now(), xxx.valid_from, xxx.valid_till, xxx.geometry from (
select aa.building_id, cba.building_id as address_building_id, aa.building_no, aa.address_khashaa, aa.au2, aa.valid_from, aa.valid_till, aa.geometry from data_soums_union.ca_building_tbl aa 
left join data_address.ca_building_address cba on aa.building_id = cba.building_id 
where substring(aa.au2, 1, 3) = '081'
)xxx where address_building_id is null