insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, valid_from, valid_till)

select pp.id, true, 1, null, null, p.address_khashaa, p.address_streetname, p.address_neighbourhood, null, substring(p.au2, 1, 3), p.au2, p.au3, 1, p.valid_from, p.valid_till from data_soums_union.ca_parcel_tbl p
join data_address.ca_parcel_address pp on p.parcel_id = pp.parcel_id

----------

insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, valid_from, valid_till)
select p.id, true, 1, null, null, p.address_parcel_no, p.address_streetname, p.address_neighbourhood, p.address_neighbourhood, substring(p.au2, 1, 3), p.au2, p.au3, 1, p.valid_from, p.valid_till from data_address.ca_parcel_address p

---------------------

insert into data_address.ca_building_address_history(building_id, is_active, in_source, street_id, address_building_no, au1, au2, sort_value, created_at, valid_from, valid_till)

select pp.id, true, 1, null, p.address_khashaa, substring(p.au2, 1, 3), p.au2, 1, p.valid_from, p.valid_from, p.valid_till from data_soums_union.ca_building_tbl p
join data_address.ca_building_address pp on p.building_id = pp.building_id
