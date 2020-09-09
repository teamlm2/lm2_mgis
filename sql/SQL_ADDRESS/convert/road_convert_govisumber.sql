---st_road
insert into data_address.st_road(code, name, street_code, street_name, is_active, max_speed, lanes, surface, highway, line_geom)
select au2.code||lpad((row_number() over(partition by au2.code))::text, 5, '0') as str_code, z.name, g.gudamjid, z.name, true, maxspeed::int, lanes::int, surface, highway, z.geom from data_address.aa_ubroad z
join admin_units.au_level2 au2 on st_within(st_centroid(z.geom), au2.geometry)
left join data_address.all_gudamj g on st_intersects(z.geom, g.geom) and g.gudamjner = z.name

-----
insert into data_address.st_road(code, name, name_en, street_code, street_name, is_active, max_speed, lanes, surface, highway, ref, oneway, bridge, au2, line_geom)
select au2.code||lpad((row_number() over(partition by au2.code))::text, 5, '0') as str_code, ss.name, z.name_en, ss.code, ss.name, true, maxspeed::int, lanes::int, surface, highway, ref, oneway, bridge, au2.code, z.geom from data_address.aa_ubroad z
left join admin_units.au_level2 au2 on st_within(st_centroid(z.geom), au2.geometry)
left join data_address.st_street_sub ss on st_within(st_centroid(z.geom), ss.geometry)

----------
select z.name, g.gudamjner, g.gudamjid, min(st_distance(z.geom, g.geom)) from data_address.aa_govisumber z, data_address.all_gudamj g, admin_units.au_level2 au2
where st_within(st_centroid(g.geom), au2.geometry) and au2.code = '04201' and g.gudamjner = z.name
group by z.name, g.gudamjner, g.gudamjid
limit 10

----------st_street parent
insert into data_address.st_street(code, name, description, is_active, street_type_id, au1, au2, au3, parent_id, street_shape_id)
select null, g.gudamjner, g.gudamjner, true, 2, au1.code, au2.code, au3.code, null, 3 from data_address.all_gudamj g
join admin_units.au_level1 au1 on st_within(st_centroid(g.geom), au1.geometry)
join admin_units.au_level2 au2 on st_within(st_centroid(g.geom), au2.geometry)
join admin_units.au_level3 au3 on st_within(st_centroid(g.geom), au3.geometry)
where  au1.code = '042'
group by g.gudamjner, g.gudamjner, au1.code, au2.code, au3.code
----------st_street child

insert into data_address.st_street (code, name, description, is_active, street_type_id, au1, au2, au3, parent_id, street_shape_id)

select g.gudamjid, g.gudamjner, g.gudamjner, true, 2, au1.code, au2.code, au3.code, s.id, 3 from data_address.all_gudamj g
join admin_units.au_level1 au1 on st_within(st_centroid(g.geom), au1.geometry)
join admin_units.au_level2 au2 on st_within(st_centroid(g.geom), au2.geometry)
join admin_units.au_level3 au3 on st_within(st_centroid(g.geom), au3.geometry)
join data_address.st_street s on s.name = g.gudamjner and s.au2 = au2.code
where  au1.code = '042'
order by g.gudamjner, g.gudamjid
ON CONFLICT (code, name, parent_id) DO nothing

----------update st_road street_id

WITH s AS (
select s.id as str_id, r.id as road_id, street_code, street_name, s.au2 from data_address.st_road r, data_address.st_street s 
where substring(r.au2, 1, 3) = '011' and street_code || '-' || street_name = s.code || '-' || s.name and s.au1 = '011'
)
UPDATE data_address.st_road
SET street_id = s.str_id
from s 
where data_address.st_road.id = s.road_id;