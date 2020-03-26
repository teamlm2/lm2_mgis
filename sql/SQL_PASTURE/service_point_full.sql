select
  au1.code, au1.name, au2.code, au2.name, au3.code, au3.name,
  pb.code, pb.group_name, pb.area_ga,
  pp.parcel_id, pp.area_ga, pp.pasture_type,
  d.*,
  t.*
  --point_detail_id, monitoring_year, register_date, area_ga, duration, rc, rc_precent, sheep_unit, sheep_unit_plant,
  --biomass, d1, d1_100ga, d2, d3, d3_rc, unelgee, rc_id, begin_month, end_month
from pasture.ps_point_d_value as t
join pasture.ps_point_detail d on t.point_detail_id = d.point_detail_id

join pasture.ps_point_detail_points dp on d.point_detail_id = dp.point_detail_id
join pasture.ca_pasture_monitoring p on dp.point_id = p.point_id
join data_soums_union.ca_pug_boundary pb on st_within(p.geometry, pb.geometry)
join data_soums_union.ca_pasture_parcel_tbl pp on st_within(p.geometry, pp.geometry)
join admin_units.au_level2 au2 on st_within(p.geometry, au2.geometry)
join admin_units.au_level1 au1 on st_within(p.geometry, au1.geometry)
join admin_units.au_level3 au3 on st_within(p.geometry, au3.geometry)
where pp.group_type = 1 and t.monitoring_year = 2019 and au2.code = '06404'
      and (LOWER(pp.pasture_type) ilike '%өвөл%' or LOWER(pp.pasture_type) ilike '%хавар%')