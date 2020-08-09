----zip code
insert into data_address.au_zipcode_area(code, description, area_m2, geometry)
select code::int, code, area_m2_utm, geometry from khayag.zipcode_area
--where code::int = 0

--------------------cadastre parcel addres

--delete from data_address.ca_parcel_address;


insert into data_address.ca_parcel_address(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, 
status, parcel_type, geometry, valid_from, valid_till)

select p.parcel_id, true, 1, null, null, address_khashaa, address_streetname, address_neighbourhood, null, substring(au2, 1, 3), au2, au3, 1, 1, 1, geometry, valid_from, valid_till from data_soums_union.ca_parcel_tbl p
--join data_address.au_zipcode_area z on st_within(st_centroid(p.geometry), z.geometry)
where p.parcel_id not in ( select parcel_id from data_address.ca_parcel_address)--substring(p.au2, 1, 3) = '048'

--------------------khayag parcel addres

insert into data_address.ca_parcel_address(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, created_at)

select p.parcel_id, false, 2, pa.zipcode_id, null, h.dugaar, h.gudamjner, null, null, substring(p.au2, 1, 3), p.au2, p.au3, 2, to_char(now(), 'yyyy-MM-dd')::date from data_address.aa_dundgovi_hashaa h , data_soums_union.ca_parcel_tbl p, data_address.ca_parcel_address pa
where st_within(st_centroid(p.geometry), h.geom) and pa.parcel_id = p.parcel_id
and substring(p.au2, 1, 3) = '048'

--------------------
--------------------cadastre building addres

delete from data_address.ca_building_address;
insert into data_address.ca_building_address(building_id, parcel_id, is_active, in_source, zipcode_id, street_id, address_building_no, au1, au2, sort_value, created_at, status, parcel_type, geometry, valid_from, valid_till)

select p.building_id, n.parcel_id, true, 1, z.id, null, p.address_khashaa, substring(p.au2, 1, 3), p.au2, 1, p.valid_from, 1, 8, p.geometry, p.valid_from, p.valid_till
from data_soums_union.ca_building_tbl p
join data_address.au_zipcode_area z on st_within(st_centroid(p.geometry), z.geometry)
left join data_soums_union.ca_parcel_tbl n on st_within(st_centroid(p.geometry), n.geometry)
where p.au2 is not null

--------------------khayag building addres

insert into data_address.ca_building_address(building_id, parcel_id, is_active, in_source, zipcode_id, street_id, building_name, address_building_no, address_streetname, au1, au2, sort_value, created_at)

select p.building_id, pa.parcel_id, false, 2, pa.zipcode_id, null, h.ner, h.baishdugaa, h.gudamjner, substring(p.au2, 1, 3), p.au2, 2, to_char(now(), 'yyyy-MM-dd')::date 
from data_address.aa_dundgovi_barilga h , data_soums_union.ca_building_tbl p, data_address.ca_building_address pa
where st_within(st_centroid(p.geometry), h.geom) and pa.building_id = p.building_id
and substring(p.au2, 1, 3) = '048'

select count(parcel_id) from data_soums_union.ca_parcel_tbl p
where substring(p.au2, 1, 3) = '048'

select count(p.parcel_id)  from data_soums_union.ca_parcel_tbl p
join data_address.au_zipcode_area z on st_within(st_centroid(p.geometry), z.geometry)
where substring(p.au2, 1, 3) = '048'

alter table data_soums_union.ca_parcel_tbl add column au3 varchar(8)

select * from data_address.ca_parcel_address
where in_source = 1