insert into data_address.ca_parcel_address(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, 
status, parcel_type, geometry, valid_from, valid_till)

select p.parcel_id, true, 1, null, null, address_khashaa, address_streetname, address_neighbourhood, null, substring(au2, 1, 3), au2, au3, 1, 1, 1, geometry, valid_from, valid_till from data_soums_union.ca_parcel_tbl p
where now() between p.valid_from and p.valid_till and p.parcel_id not in ( select parcel_id from data_address.ca_parcel_address p where p.au2 = '01101') and p.au2 = '01101'--and substring(p.au2, 1, 3) = '048'
--ON CONFLICT (parcel_id) DO NOTHING;



------history
insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, valid_from, valid_till)

select pp.id, true, 1, null, null, p.address_khashaa, p.address_streetname, p.address_neighbourhood, null, substring(p.au2, 1, 3), p.au2, p.au3, 1, p.valid_from, p.valid_till from data_soums_union.ca_parcel_tbl p
join data_address.ca_parcel_address pp on p.parcel_id = pp.parcel_id
ON CONFLICT ON CONSTRAINT ca_parcel_address_history_parcel_id_fkey DO NOTHING;


ALTER TABLE data_address.ca_parcel_address ADD CONSTRAINT ca_parcel_address_unique_cols UNIQUE (parcel_id, parcel_type, is_active, created_at);

select id, parcel_id,  from data_address.ca_parcel_address
where parcel_id = '2106026519'
order by created_at desc