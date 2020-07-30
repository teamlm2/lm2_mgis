select au1.code as au1_code, au1.name as au1_name, au2.code as au2_code, au2.name as au2_name,
au3.code as au3_code, au3.name as au3_name
,za.code as zip_code
,case 
	when parcel.street_id is not null then (select name from data_address.st_street where id = parcel.street_id)
	when sz.id is not null then (select name from data_address.st_street s group by s.name order by min(st_distance(s.line_geom, (GeomFromEWKT('SRID=4326;POINT(106.89120 47.93003)')))) asc limit 1)
	when sz.id is null then 'gazarzuin ner'
	else ''
end as street_name,
parcel.address_parcel_no,
building.address_building_no

 from (SELECT (GeomFromEWKT('SRID=4326;POINT(106.89120 47.93003)')) as geom)pc
join admin_units.au_level1 au1 on st_within(pc.geom, au1.geometry)
join admin_units.au_level2 au2 on st_within(pc.geom, au2.geometry)
join admin_units.au_level3 au3 on st_within(pc.geom, au3.geometry)
left join admin_units.au_settlement_zone_view sz on st_within(pc.geom, sz.geometry)
left join data_address.ca_parcel_address parcel on st_within(pc.geom, parcel.geometry)
left join data_address.ca_building_address building on st_within(pc.geom, building.geometry)
left join data_address.au_zipcode_area za on st_within(pc.geom, za.geometry)

