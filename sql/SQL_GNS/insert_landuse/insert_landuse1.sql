delete from data_landuse.ca_landuse_type4_tbl;

insert into data_landuse.ca_landuse_type4_tbl(landuse, landuse_level1, landuse_level2, geometry, au1, au2, au3)
select landuse, landuse_level1, landuse_level2, geometry, au1, au2, au3 from data_landuse.ca_landuse_type_tbl