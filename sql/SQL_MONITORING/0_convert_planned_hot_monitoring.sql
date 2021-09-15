----main parcel

insert into data_monitoring.mt_monitor_parcel(code, landuse_real, address_neighbourhood, is_active, monitor_parcel_type_id, geometry, monitor_type_id)

select au2.code||'-02-'||LPAD(row_number() over(partition by au2.code)::text, 5, '0')||'-19', 2, au1_name ||', '|| au2_name ||', '|| au3_name, true, 1, ((ST_DUMP(geom)).geom)::geometry(Polygon,4326), 2 from data_monitoring.aa_main_par p
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)

----sub_parcel

insert into data_monitoring.mt_monitor_parcel(code, landuse_real, address_neighbourhood, is_active, monitor_parcel_type_id, geometry, monitor_type_id)

select au2.code||'-02-'||LPAD(row_number() over(partition by au2.code)::text, 5, '0')||'-19', lcode2, au1_name ||', '|| au2_name ||', '|| au3_name, true, 2, ((ST_DUMP(geom)).geom)::geometry(Polygon,4326), 2 from data_monitoring.aa_sub_par p
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)

----update main parcel id

with new_numbers as (
select sub.monitor_parcel_id, main.monitor_parcel_id as main_parcel_id from data_monitoring.mt_monitor_parcel main, (select monitor_parcel_id, geometry, monitor_parcel_type_id, au2 from data_monitoring.mt_monitor_parcel) as sub
where st_within(st_centroid(sub.geometry), main.geometry) and sub.au2 = '04410' and sub.monitor_parcel_type_id = 2 and main.monitor_parcel_type_id = 1
)
update data_monitoring.mt_monitor_parcel set main_parcel_id = s.main_parcel_id
from new_numbers s
where data_monitoring.mt_monitor_parcel.monitor_parcel_id = s.monitor_parcel_id;

----monitoringiin burtgel uusgeh

insert into data_monitoring.mt_monitoring(code, name, monitor_type_id, workrule_status_id, au2, landuse_real)

select '04410-'||'1-'||LPAD(row_number() over()::text, 5, '0'), au1_name ||', '|| au2_name ||', '|| au3_name || ' /төлөвлөгөөт хянан баталгаа/', 2, 56, '04410', 2 from data_monitoring.aa_sub_par

----monitoring main parcel map
insert into data_monitoring.mt_monitoring_parcel_map(monitoring_id, monitor_parcel_id)

select monitoring_id, p.monitor_parcel_id from data_monitoring.mt_monitoring m, data_monitoring.mt_monitor_parcel p
where m.au2 = '04410' and m.code = p.code and p.monitor_parcel_type_id = 1

----monitoring sub parcel map
insert into data_monitoring.mt_monitoring_parcel_map(monitoring_id, monitor_parcel_id)
select monitoring_id, p.monitor_parcel_id from data_monitoring.mt_monitoring m, (select main.code, sub.monitor_parcel_id, sub.monitor_parcel_type_id from data_monitoring.mt_monitor_parcel main, data_monitoring.mt_monitor_parcel sub
where main.monitor_parcel_id = sub.main_parcel_id) p
where m.au2 = '04410' and m.code = p.code and p.monitor_parcel_type_id = 2

----tuluvluguut hyanan batalgaa bolgoh
insert into data_monitoring.mt_verify_planned(monitoring_id, landuse, landuse_real)

select monitoring_id, 2, 2 from data_monitoring.mt_monitoring 
where au2 = '04410' and monitor_type_id = 2

----monitoringiin tseg
insert into data_monitoring.mt_monitor_point(code, is_active, monitor_point_type_id, geometry)

select '04410-'||'003-'||LPAD(row_number() over()::text, 5, '0'), true, 3, ((ST_DUMP(geom)).geom)::geometry(Point,4326) from data_monitoring.aa_moni_pnt

----soil tseg
insert into data_monitoring.mt_monitor_point(code, is_active, monitor_point_type_id, geometry)

select '04410-'||'001-'||LPAD(row_number() over()::text, 5, '0'), true, 1, ((ST_DUMP(geom)).geom)::geometry(Point,4326) from data_monitoring.aa_soil_pnt

----data_monitoring.mt_monitoring_point_map
insert into data_monitoring.mt_monitoring_point_map(monitor_point_id, monitoring_id)

select p.monitor_point_id, m.monitoring_id from data_monitoring.mt_monitoring_parcel_map map
join data_monitoring.mt_monitoring m on map.monitoring_id = m.monitoring_id
join data_monitoring.mt_monitor_parcel parcel on parcel.monitor_parcel_id = map.monitor_parcel_id
join data_monitoring.mt_monitor_point p on st_within(p.geometry, parcel.geometry)
where m.au2 = '04410' and m.monitor_type_id = 2
group by p.monitor_point_id, m.monitoring_id

----data_monitoring.mt_set_monitor_parcel_monitor_point
insert into data_monitoring.mt_set_monitor_parcel_monitor_point(monitor_point_id, monitor_parcel_id)

select p.monitor_point_id, parcel.monitor_parcel_id from data_monitoring.mt_monitoring_parcel_map map
join data_monitoring.mt_monitoring m on map.monitoring_id = m.monitoring_id
join data_monitoring.mt_monitor_parcel parcel on parcel.monitor_parcel_id = map.monitor_parcel_id
join data_monitoring.mt_monitor_point p on st_within(p.geometry, parcel.geometry)
where m.au2 = '04410' and m.monitor_type_id = 2
group by p.monitor_point_id, parcel.monitor_parcel_id, m.monitoring_id



select * from data_monitoring.aa_sub_par
