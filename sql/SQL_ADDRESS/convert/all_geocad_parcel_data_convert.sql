select count(*) from data_address.all_khashaa h
where gid not in (select h.gid from data_address.all_khashaa h
join data_address.ca_parcel_address pa on ST_Intersects(pa.geometry, h.geom) group by h.gid)

 SELECT count(*) FROM data_address.all_khashaa hp
  WHERE NOT EXISTS (
    SELECT 1 FROM data_address.ca_parcel_address AS par WHERE ST_Overlaps(hp.geom, par.geometry));


--------------------khayag parcel addres HISTORY
insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, address_street_code, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, created_at)

select pa.id, false, 2, pa.zipcode_id, null, h.dugaar, h.gudamjner, null, null, substring(pa.au2, 1, 3), pa.au2, pa.au3, 2, to_char(now(), 'yyyy-MM-dd')::date 
from data_address.all_khashaa h , data_address.ca_parcel_address pa
where st_within(st_centroid(pa.geometry), h.geom) 
--and pa.parcel_id = p.parcel_id
--and substring(pa.au2, 1, 3) = '048'


--------------------cadastre parcel addres HISTORY
insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, street_id, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, created_at)

select pa.id, true, 1, null, null, pa.street_id, p.address_khashaa, p.address_streetname, p.address_neighbourhood, null, substring(p.au2, 1, 3), p.au2, p.au3, 1, to_char(now(), 'yyyy-MM-dd')::date  
from data_soums_union.ca_parcel_tbl p, data_address.ca_parcel_address pa
--join data_address.au_zipcode_area z on st_within(st_centroid(p.geometry), z.geometry)
where pa.parcel_id = p.parcel_id 
--and substring(p.au2, 1, 3) = '048'
--and p.parcel_id not in ( select parcel_id from data_address.ca_parcel_address)--substring(p.au2, 1, 3) = '048'


--------------------

insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, zipcode_id, address_street_code, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, created_at)
select id, true, 2, null, street_code, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, 2, created_at from data_address.ca_parcel_address where parcel_type = 7

--------------------
insert into data_address.ca_parcel_address_history
(parcel_id, is_active, in_source, zipcode_id, address_street_code, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, au1, au2, au3, sort_value, created_at)

select p.id, true, 2, null, bz.street_code, bz.address_parcel_no, bz.address_streetname, bz.address_neighbourhood, bz.geographic_name, bz.au1, bz.au2, bz.au3, 2, bz.created_at from (select * from data_address.ca_parcel_address
where parcel_type = 7 and au2 = '04201') as bz, (select id, geometry from data_address.ca_parcel_address
where parcel_type = 1 and au2 = '04201' and is_new_address = true and now() between '1900-01-01'::date and valid_till) p
where st_within(st_centroid(bz.geometry), p.geometry)




