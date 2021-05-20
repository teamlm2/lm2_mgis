with new_numbers as (
select row_number() over(partition by aa.geo_id, aa.landuse) as p_no, aa.id as parcel_id, aa.landuse, aa.description, aa.geo_id, gg.text, gg.geo_data, aa.geometry, st_distance(aa.geometry, bb.geometry)
from (
select a.id, a.parcel_id, a.landuse, cl.description, a.geometry, (select * from base.gn_get_parcel_geo_id(a.geometry)) from data_address.ca_parcel_address a
join codelists.cl_landuse_type cl on a.landuse = cl.code
join (select ST_Union(b.geometry) as geometry, au2.code as au2_code from admin_units.au_settlement_zone_view b
join admin_units.au_level2 au2 on st_within(st_centroid(b.geometry), au2.geometry)
where au2.code = '04401' group by au2.code) b on not st_intersects(a.geometry, b.geometry)
where a.street_id is null and a.au2 = '04401' and b.au2_code = '04401' --and a.parcel_id = '4410004196' limit 10 and a.parcel_id in ('8116000786', '8116000592', '8116000764', '8116000599')
)aa, (select * from data_address.au_settlement_zone_point bb
where bb.au2 = '04401' and bb.is_address is true limit 1) bb, data_address_import.gn_soft gg
where gg.geo_id = aa.geo_id and bb.au2 = '04401' and bb.is_address is true
order by aa.geo_id, st_distance(aa.geometry, bb.geometry) asc
)
update data_address.ca_parcel_address
set gn_geo_id = s.geo_id, geographic_name = s.text, address_streetname = s.text, address_parcel_no = s.p_no, in_source = 9
from new_numbers s
where data_address.ca_parcel_address.id = s.parcel_id;