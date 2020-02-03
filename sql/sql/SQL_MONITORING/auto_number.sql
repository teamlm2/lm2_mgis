select au2.code, max((split_part(aa.code, '-', 3))::int) from data_monitoring.aa_main_par p 
join admin_units.au_level2 au2 on st_within(st_centroid(p.geom), au2.geometry)
join (select p.code, au2.code as soum_code, p.monitor_type_id  from data_monitoring.mt_monitor_parcel p
join admin_units.au_level2 au2 on st_within(st_centroid(p.geometry), au2.geometry)) aa on au2.code = aa.soum_code
where split_part(aa.code, '-', 4) = '19'
group by au2.code


data_monitoring.mt_monitor_parcel