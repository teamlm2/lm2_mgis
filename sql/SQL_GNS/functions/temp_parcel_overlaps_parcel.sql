select p.parcel_id, p.area_m2, p.landuse from data_landuse.ca_tmp_landuse_type_tbl t
join data_landuse.ca_landuse_type_tbl p on st_overlaps(t.geometry, p.geometry)
where t.parcel_id = 8

------------------

DROP FUNCTION base.landuse_temp_parcel_overlaps(integer);

CREATE OR REPLACE FUNCTION base.landuse_temp_parcel_overlaps(tmp_parcel_id integer)
    RETURNS TABLE(parcel_id integer, area_m2 numeric, landuse integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$

DECLARE
	v_utmsrid integer;
BEGIN
    
	RETURN  query select p.parcel_id, p.area_m2, p.landuse from data_landuse.ca_tmp_landuse_type_tbl t
			join data_landuse.ca_landuse_type_tbl p on st_intersects(t.geometry, p.geometry)
			where t.parcel_id = tmp_parcel_id;

END;

$BODY$;

ALTER FUNCTION base.landuse_temp_parcel_overlaps(integer)
    OWNER TO geodb_admin;

select base.landuse_temp_parcel_overlaps(8)

