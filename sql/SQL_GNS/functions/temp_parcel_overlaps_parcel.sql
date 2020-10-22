select row_number() over() as gid, p.parcel_id, base.calculate_area_utm(st_intersection(t.geometry, p.geometry)) as overlaps_area_m2, p.landuse from data_landuse.ca_tmp_landuse_type_tbl t
			join data_landuse.ca_landuse_type_tbl p on st_intersects(t.geometry, p.geometry)
			where t.parcel_id = 8;

--
select row_number() over() as gid, p.parcel_id, base.calculate_area_utm(st_intersection(t.geometry, p.geometry)) as overlaps_area_m2, p.landuse from data_landuse.ca_tmp_landuse_type_tbl t
join data_landuse.ca_landuse_type_tbl p on st_intersects(t.geometry, p.geometry)
join data_landuse.ca_landuse_maintenance_case c on t.case_id = c.id
where c.id  = 5
--

------------------

DROP FUNCTION if exists base.landuse_temp_parcel_overlaps(integer);

CREATE OR REPLACE FUNCTION base.landuse_temp_parcel_overlaps(tmp_parcel_id integer)
    RETURNS TABLE(gid bigint, parcel_id integer, area_m2 numeric, landuse integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$

DECLARE
	v_utmsrid integer;
BEGIN
    
	RETURN  query select row_number() over() as gid, p.parcel_id, base.calculate_area_utm(st_intersection(t.geometry, p.geometry))::numeric as overlaps_area_m2, p.landuse from data_landuse.ca_tmp_landuse_type_tbl t
			join data_landuse.ca_landuse_type_tbl p on st_intersects(t.geometry, p.geometry)
			where t.parcel_id = tmp_parcel_id;

END;

$BODY$;

ALTER FUNCTION base.landuse_temp_parcel_overlaps(integer)
    OWNER TO geodb_admin;

select base.landuse_temp_parcel_overlaps(8)

