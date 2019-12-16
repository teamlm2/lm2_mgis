----sub_parcel

insert into data_monitoring.mt_monitor_parcel(code, landuse_real, address_neighbourhood, is_active, monitor_parcel_type_id, geometry, monitor_type_id, convert_id, old_parcel_id)

select au2.code||'-02-'||LPAD(row_number() over(partition by au2.code)::text, 5, '0')||'-18', p.* from 
( 
select map.landuse_code::int, gaz_name, true, 2, ((ST_DUMP(geom)).geom)::geometry(Polygon,4326) as geom, 2, convert_id,  par_num from data_monitoring.aa_tarailan_polygon_2018 p
join data_monitoring.aa_tarialan_landuse_map map on p.l_code34::text = map.code
)p
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)
where st_isvalid(p.geom) = true order by au2.code

----monitoringiin burtgel uusgeh

insert into data_monitoring.mt_monitoring(code, name, monitor_type_id, workrule_status_id, au2, landuse_real, convert_id)

select au2.code||'-02-'||LPAD(row_number() over(partition by au2.code)::text, 5, '0')||'-18', p.gaz_name || ' /төлөвлөгөөт хянан баталгаа/', 2, 56, au2.code, map.landuse_code::int, convert_id from data_monitoring.aa_tarailan_polygon_2018 p
left join data_monitoring.aa_tarialan_landuse_map map on p.l_code34::text = map.code
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)
where st_isvalid(p.geom) = true

----monitoring sub parcel map
insert into data_monitoring.mt_monitoring_parcel_map(monitoring_id, monitor_parcel_id)

select m.monitoring_id, p.monitor_parcel_id from data_monitoring.aa_tarailan_polygon_2018 d
join data_monitoring.mt_monitoring m on d.convert_id = m.convert_id
join data_monitoring.mt_monitor_parcel p on m.convert_id = p.convert_id
--on conflict(monitoring_id, monitor_parcel_id) do nothing;

----tuluvluguut hyanan batalgaa bolgoh
insert into data_monitoring.mt_verify_planned(monitoring_id, landuse, landuse_real)

select m.monitoring_id, map.landuse_code::int, map.landuse_code::int from data_monitoring.aa_tarailan_polygon_2018 d
join data_monitoring.mt_monitoring m on d.convert_id = m.convert_id
join data_monitoring.mt_monitor_parcel p on m.convert_id = p.convert_id
left join data_monitoring.aa_tarialan_landuse_map map on d.l_code34::text = map.code
on conflict(monitoring_id) do nothing;




-----------------------------------

----soil tseg
insert into data_monitoring.mt_monitor_point(code, is_active, monitor_point_type_id, geometry, convert_id)

select au2.code||'-001-'||LPAD(row_number() over()::text, 5, '0')||'-18', true, 1, ((ST_DUMP(geom)).geom)::geometry(Point,4326), convert_id from data_monitoring.aa_tarailan_point_2018 p
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)

----data_monitoring.mt_monitoring_point_map
insert into data_monitoring.mt_monitoring_point_map(monitor_point_id, monitoring_id)

select p.monitor_point_id, m.monitoring_id from data_monitoring.mt_monitoring_parcel_map map
join data_monitoring.mt_monitoring m on map.monitoring_id = m.monitoring_id
join data_monitoring.mt_monitor_parcel parcel on parcel.monitor_parcel_id = map.monitor_parcel_id
join data_monitoring.mt_monitor_point p on st_within(p.geometry, parcel.geometry)
where m.convert_id is not null 
--m.au2 = '04410' and m.monitor_type_id = 2
group by p.monitor_point_id, m.monitoring_id
on conflict(monitor_point_id, monitoring_id) do nothing;

----data_monitoring.mt_set_monitor_parcel_monitor_point
insert into data_monitoring.mt_set_monitor_parcel_monitor_point(monitor_point_id, monitor_parcel_id)

select p.monitor_point_id, parcel.monitor_parcel_id from data_monitoring.mt_monitoring_parcel_map map
join data_monitoring.mt_monitoring m on map.monitoring_id = m.monitoring_id
join data_monitoring.mt_monitor_parcel parcel on parcel.monitor_parcel_id = map.monitor_parcel_id
join data_monitoring.mt_monitor_point p on st_within(p.geometry, parcel.geometry)
where m.convert_id is not null  
--m.au2 = '04410' and m.monitor_type_id = 2
group by p.monitor_point_id, parcel.monitor_parcel_id, m.monitoring_id
on conflict(monitor_point_id, monitor_parcel_id) do nothing;



select * from data_monitoring.aa_tarailan_polygon_2018
