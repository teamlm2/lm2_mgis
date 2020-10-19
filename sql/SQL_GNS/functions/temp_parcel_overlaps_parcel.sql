select t.parcel_id, p.parcel_id from data_landuse.ca_tmp_landuse_type_tbl t
join data_landuse.ca_landuse_type_tbl p on st_overlaps(t.geometry, p.geometry)
where t.parcel_id = 8