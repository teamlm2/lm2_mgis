
--------------------khayag building addres

insert into data_address.ca_building_address_history(building_id, is_active, in_source, zipcode_id, street_id, building_name, address_building_no, address_streetname, au1, au2, sort_value, created_at)

select pa.id, false, 2, pa.zipcode_id, null, h.ner, h.baishdugaa, h.gudamjner, substring(pa.au2, 1, 3), pa.au2, 2, to_char(now(), 'yyyy-MM-dd')::date 
from data_address.all_barilga h , data_address.ca_building_address pa
where st_within(st_centroid(pa.geometry), h.geom) 
--and pa.building_id = p.building_id
--and substring(pa.au2, 1, 3) = '048'

--------------------cadastre building addres

--delete from data_address.ca_building_address_history;
insert into data_address.ca_building_address_history(building_id, is_active, in_source, zipcode_id, street_id, address_building_no, au1, au2, sort_value, created_at)

select pa.id, true, 1, null, null, p.address_khashaa, substring(p.au2, 1, 3), p.au2, 1, to_char(now(), 'yyyy-MM-dd')::date 
from data_soums_union.ca_building_tbl p, data_address.ca_building_address pa
--join data_address.au_zipcode_area z on st_within(st_centroid(p.geometry), z.geometry)
--left join data_soums_union.ca_parcel_tbl n on st_within(st_centroid(p.geometry), n.geometry)
where pa.building_id = p.building_id 
