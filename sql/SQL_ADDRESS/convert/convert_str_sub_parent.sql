--alter table data_address.st_street alter column geometry type geometry(Polygon,4326);
ALTER TABLE data_address.st_street ADD CONSTRAINT st_street_unique UNIQUE (code, name, parent_id);

--delete from data_address.st_street where parent_id is not null;
insert into data_address.st_street (code, name, description, is_active, in_source, street_type_id, valid_from, valid_till, geometry, au2, au3, parent_id)
select s.code, s.name, s.description, s.is_active, s.in_source, s.street_type_id, s.valid_from, s.valid_till, ST_Multi(s.geometry)::geometry(MultiPolygon,4326), s.au2, s.au3, p.id from data_address.st_street_sub s
join data_address.st_street p on st_within(st_centroid(s.geometry), p.geometry)
ON CONFLICT (code, name, parent_id) DO nothing

select count(*) from data_address.st_street