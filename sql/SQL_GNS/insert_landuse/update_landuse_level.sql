-----------6 angilalaar salgasan husnegt-------
update data_landuse.ca_landuse_type1_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type1_tbl set landuse_level2 = substring(landuse::text,1,2)::int;

update data_landuse.ca_landuse_type2_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type2_tbl set landuse_level2 = substring(landuse::text,1,2)::int;

update data_landuse.ca_landuse_type3_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type3_tbl set landuse_level2 = substring(landuse::text,1,2)::int;

update data_landuse.ca_landuse_type6_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type6_tbl set landuse_level2 = substring(landuse::text,1,2)::int;

update data_landuse.ca_landuse_type4_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 41 where landuse != 4101;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 42 where landuse != 4102;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 43 where landuse != 4103;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 44 where landuse != 4104;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 45 where landuse != 4105;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 46 where landuse != 4106;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 47 where landuse != 4107;
update data_landuse.ca_landuse_type4_tbl set landuse_level2 = 48 where landuse != 4108;

update data_landuse.ca_landuse_type5_tbl set landuse_level1 = substring(landuse::text,1,1)::int;
update data_landuse.ca_landuse_type5_tbl set landuse_level2 = 51 where landuse != 5101;
update data_landuse.ca_landuse_type5_tbl set landuse_level2 = 52 where landuse != 5102;
update data_landuse.ca_landuse_type5_tbl set landuse_level2 = 53 where landuse != 5103;
update data_landuse.ca_landuse_type5_tbl set landuse_level2 = 54 where landuse != 5104;

-----------negdsen husnegt-------
update data_landuse.ca_parcel_landuse_tbl set landuse_level1 = substring(landuse::text,1,1)::int;

--------

update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = substring(landuse::text,1,2)::int 
where landuse_level2 != 4 and landuse_level2 != 5;

-------oin san, usan san gazriin level2-g daraah baidlaar oruulna

update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 41 where landuse != 4101;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 42 where landuse != 4102;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 43 where landuse != 4103;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 44 where landuse != 4104;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 45 where landuse != 4105;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 46 where landuse != 4106;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 47 where landuse != 4107;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 48 where landuse != 4108;

update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 51 where landuse != 5101;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 52 where landuse != 5102;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 53 where landuse != 5103;
update data_landuse.ca_parcel_landuse_tbl set landuse_level2 = 54 where landuse != 5104;

select landuse_level1, landuse, substring(landuse::text,1,1) from data_landuse.ca_parcel_landuse_tbl
limit 10