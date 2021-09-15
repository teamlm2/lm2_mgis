CREATE MATERIALIZED VIEW data_soums_union.aa_parcel_address AS 
select row_number() over() as gid, p.parcel_id,  g.new_addr_1, g.new_addres, g.new_khasha, p.address_streetname, p.address_khashaa, p.au2, p.geometry from data_soums_union.ca_parcel_tbl p
--left join data_ub.ca_ub_parcel_tbl u on st_within(st_centroid(p.geometry), u.geometry) 
left join data_address.all_khashaa_last g on st_within(st_centroid(p.geometry), g.geom) 
where substring(p.au2, 1, 3) = '011' ;
ALTER TABLE data_soums_union.aa_parcel_address
  OWNER TO geodb_admin;


CREATE MATERIALIZED VIEW data_soums_union.aa_ub_parcel_address AS 
select row_number() over() as gid, p.old_parcel_id,  g.new_addr_1, g.new_addres, g.new_khasha, p.address_streetname, p.address_khashaa, p.au2, p.geometry from data_ub.ca_ub_parcel_tbl p
join data_ub.all_subject s on p.old_parcel_id = s.oldpid
left join data_address.all_khashaa_last g on st_within(st_centroid(p.geometry), g.geom) 
where substring(p.au2, 1, 3) = '011' and s.is_finish IS NULL;
ALTER TABLE data_soums_union.aa_ub_parcel_address
  OWNER TO geodb_admin;


--select count(parcel_id) from data_soums_union.ca_parcel_tbl p where substring(p.au2, 1, 3) = '011' 

CREATE MATERIALIZED VIEW data_soums_union.aa_building_address AS 
select row_number() over() as gid, p.building_id,  g.new_street as n_street_id, g.new_stre_1 as n_street_name, g.new_buildi as n_build_name, g.new_buil_1 as n_build_no, p.building_no, p.address_streetname, p.address_khashaa, p.au2, p.geometry from data_soums_union.ca_building_tbl p
left join data_address.all_barilga_last g on st_within(st_centroid(p.geometry), g.geom) 
where substring(p.au2, 1, 3) = '011' ;
ALTER TABLE data_soums_union.aa_building_address
  OWNER TO geodb_admin;