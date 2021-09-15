insert into data_landuse.ca_landuse_type4_tbl (landuse, geometry)
select landuse, geometry from data_landuse.ca_parcel_landuse_tbl 
where substring(landuse::text,1,1)::int = 4