
update data_monitoring.mt_monitor_parcel set area_m2 = st_area(st_transform(geometry, base.find_utm_srid(st_centroid(geometry)))) 
where st_y(st_centroid(geometry)) < 200 and area_m2 is null 