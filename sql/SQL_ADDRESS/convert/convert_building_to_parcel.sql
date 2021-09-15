insert into data_address.ca_parcel_address(parcel_id, is_active, parcel_type, in_source, status, address_parcel_no, address_streetname, au1, au2, sort_value, geometry, valid_from, valid_till)
select cba2.id, true, 11, 9, 1, address_building_no, address_streetname, al.au1_code, al.code, 1, cba2.geometry, cba2.valid_from, cba2.valid_till from data_address.ca_building_address cba2
join admin_units.au_level2 al on cba2.au2 = al.code 
where cba2.au2 = '01125' and cba2.id not in
(select cba.id from data_address.ca_building_address cba, data_address.ca_parcel_address cpa
where cba.au2 = '01125' and cpa.au2 = '01125' and (st_overlaps(cpa.geometry, cba.geometry) or st_covers(cpa.geometry, cba.geometry))
group by cba.id)