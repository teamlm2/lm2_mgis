alter table data_address.st_road add column road_id int;

create table data_address.st_road_old as
  select * from data_address.st_road
with data;

--insert road
delete from data_address.st_road;
insert into data_address.st_road(road_id, name, street_code, street_name, is_active, max_speed, lanes, surface, highway, line_geom)
select cad_id, name, gudamjid, gudamjner, true, maxspeed::int, lanes::int, surface, highway, geom from data_address.a_road

--update road street_id
with new_v as (
select o.cad_id, r.street_id from data_address.st_road_old r
join data_address.a_road o on ST_intersects(o.geom, r.line_geom)
where r.street_id is not null
)
update data_address.st_road set street_id = road.street_id
from new_v road
where data_address.st_road.road_id = road.cad_id;


-----------------
select count(r.id) from data_address.st_road r
join data_address.a_road o on ST_intersects(o.geom, r.line_geom)
where r.street_id is not null

select * from data_address.a_road
limit 1000


select count(r.id) from data_address.st_road r
join data_address.st_street s on r.street_id = s.id
join data_address.a_road o on s.name = o.gudamjner and s.code = o.gudamjid
join admin_units.au_level2 au2 on st_within(st_centroid(o.geom), au2.geometry) and st_within(st_centroid(r.line_geom), au2.geometry)
where r.street_id is not null


select count(r.id) from data_address.st_road r
join data_address.st_street s on r.street_id = s.id
--join data_address.a_road o on s.name = o.gudamjner and s.code = o.gudamjid
join data_address.a_road o on st_overlaps(r.line_geom, o.geom)
--join admin_units.au_level2 au2 on st_within(st_centroid(o.geom), au2.geometry) and st_within(st_centroid(r.line_geom), au2.geometry)
where r.street_id is not null

select count(r.id) from data_address.st_road r
join data_address.a_road o on ST_Crosses(o.geom, r.line_geom)


select count(r.id) from data_address.st_road r
join data_address.a_road o on ST_intersects(o.geom, r.line_geom)
where r.street_id is not null


