DROP MATERIALIZED VIEW data_address_cd.view_parcel_joining_street_01104;
CREATE MATERIALIZED VIEW data_address_cd.view_parcel_joining_street_01104 AS 
select * from (
select cpa2.id,
(select xxx.street_id from (
select ss.id as street_id, min(st_distance(st_transform(ggg.geometry, 32648), st_transform(ss.line_geom, 32648))) min_d, ggg.geometry, ss.line_geom from (
select cpa.id, cpa.parcel_id, se.geometry from data_address.ca_parcel_address cpa
join data_address.st_entrance se on cpa.id = se.parcel_id 
where cpa.is_active is true and cpa.street_id is null and cpa.id = cpa2.id order by se."type" asc limit 1
)ggg , data_address.st_street ss
where ss.au2 = '01104'
group by ggg.geometry, ss.line_geom, ss.id
order by min(st_distance(ggg.geometry, ss.line_geom)) asc
limit 1
)xxx where min_d <= 40), cpa2.au2, cpa2.geometry
from data_address.ca_parcel_address cpa2 
where cpa2.is_active is true 
and cpa2.au2 = '01104' 
and cpa2.street_id is null and cpa2.street_side is null and cpa2.gn_geo_id is null
--limit 2
)ccc
where ccc.street_id is not null
WITH DATA;
ALTER TABLE data_address_cd.view_parcel_joining_street_01104
  OWNER TO geodb_admin;