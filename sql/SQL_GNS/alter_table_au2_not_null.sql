select count(parcel_id) from data_landuse.ca_landuse_type_tbl
where au2 is null

select p.parcel_id, p.geometry, substring(p.au2, 1, 3) from data_landuse.ca_landuse_type_tbl p
where p.au1 is null

with new_numbers as (
select p.parcel_id, p.geometry, au2.code, p.au2 from data_landuse.ca_landuse_type_tbl p
join admin_units.au_level2 au2 on st_within(ST_PointOnSurface(p.geometry), au2.geometry)
where p.au2 is null
)
update data_landuse.ca_landuse_type_tbl
  set au2 = s.code
from new_numbers s
where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id and data_landuse.ca_landuse_type_tbl.au2 is null;

update data_landuse.ca_landuse_type_tbl set au2 = aa.code from(select p.parcel_id, p.geometry, au2.code, p.au2 from data_landuse.ca_landuse_type_tbl p
join admin_units.au_level2 au2 on st_within(ST_PointOnSurface(p.geometry), au2.geometry)
where p.au2 is null) as aa where data_landuse.ca_landuse_type_tbl.parcel_id = aa.parcel_id

delete from data_landuse.ca_landuse_type_tbl where au2 is null
ALTER TABLE data_landuse.ca_landuse_type_tbl ALTER COLUMN au2 SET NOT NULL;

update data_landuse.ca_landuse_type_tbl set au1 = substring(au2, 1, 3) where au1 is null;
ALTER TABLE data_landuse.ca_landuse_type_tbl ALTER COLUMN au1 SET NOT NULL;

ALTER TABLE data_landuse.ca_landuse_type_tbl ALTER COLUMN landuse SET NOT NULL;
update data_landuse.ca_landuse_type_tbl set landuse_level1 = substring(landuse::text, 1, 1)::int where landuse_level1 is null;
ALTER TABLE data_landuse.ca_landuse_type_tbl ALTER COLUMN landuse_level1 SET NOT NULL;
update data_landuse.ca_landuse_type_tbl set landuse_level2 = substring(landuse::text, 1, 2)::int where landuse_level2 is null;
ALTER TABLE data_landuse.ca_landuse_type_tbl ALTER COLUMN landuse_level2 SET NOT NULL;