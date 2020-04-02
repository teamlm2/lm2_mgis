insert into data_landuse.ca_parcel_landuse_tbl (landuse, geometry)
select landuse,(ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom
 from data_landuse.all_gns_type_4