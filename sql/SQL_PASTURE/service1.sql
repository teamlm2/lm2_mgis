
select coalesce(aaa.rc_id, 0)::text || '-' || bbb.rc_id::text,  bbb.* from
(
  select
      au1.code as au1_code, au1.name as au1_name, au2.code as au2_code, au2.name as au2_name,
      pb.group_name, pb.area_ga as pug_area_ga, p.parcel_id, p.pasture_type, p.area_ga,
      d.point_detail_id, t.rc_id
from data_soums_union.ca_pug_boundary pb
join admin_units.au_level2 au2 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au2.geometry)
join admin_units.au_level1 au1 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au1.geometry)
join admin_units.au_level3 au3 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au3.geometry)
join data_soums_union.ca_pasture_parcel_tbl p on st_within(st_centroid(p.geometry), pb.geometry)
join pasture.ca_pasture_monitoring pm on st_within(pm.geometry, p.geometry)
join pasture.ps_point_detail_points dp on pm.point_id = dp.point_id
join pasture.ps_point_detail d on dp.point_detail_id = d.point_detail_id
JOIN pasture.ps_point_d_value t on d.point_detail_id = t.point_detail_id
where au2.code = '08110' and t.monitoring_year = 2018 --and (LOWER(p.pasture_type) ilike '%өвөл%' or LOWER(p.pasture_type) ilike '%хавар%')
GROUP BY au1.code, au1.name, au2.code, au2.name, pb.group_name, pb.area_ga, p.area_ga, p.parcel_id, p.pasture_type, d.point_detail_id, t.rc_id
ORDER BY pb.group_name
)aaa
full join (
    select
      au1.code as au1_code, au1.name as au1_name, au2.code as au2_code, au2.name as au2_name,
      pb.group_name, pb.area_ga as pug_area_ga, p.parcel_id, p.pasture_type, p.area_ga,
      d.point_detail_id, t.rc_id
from data_soums_union.ca_pug_boundary pb
join admin_units.au_level2 au2 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au2.geometry)
join admin_units.au_level1 au1 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au1.geometry)
join admin_units.au_level3 au3 on st_within(ST_PointOnSurface(ST_Makevalid(pb.geometry)), au3.geometry)
join data_soums_union.ca_pasture_parcel_tbl p on st_within(st_centroid(p.geometry), pb.geometry)
join pasture.ca_pasture_monitoring pm on st_within(pm.geometry, p.geometry)
join pasture.ps_point_detail_points dp on pm.point_id = dp.point_id
join pasture.ps_point_detail d on dp.point_detail_id = d.point_detail_id
JOIN pasture.ps_point_d_value t on d.point_detail_id = t.point_detail_id
where au2.code = '08110' and t.monitoring_year = 2019 --and (LOWER(p.pasture_type) ilike '%өвөл%' or LOWER(p.pasture_type) ilike '%хавар%')
GROUP BY au1.code, au1.name, au2.code, au2.name, pb.group_name, pb.area_ga, p.area_ga, p.parcel_id, p.pasture_type, d.point_detail_id, t.rc_id
ORDER BY pb.group_name
    )bbb on aaa.point_detail_id = bbb.point_detail_id

select * from pasture.set_rc_change st
join pasture.cl_rc_change rc on st.rc_change_id = rc.code
where value = '1-4'

