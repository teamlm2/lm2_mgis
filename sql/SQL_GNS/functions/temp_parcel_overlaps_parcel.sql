select t.parcel_id, p.parcel_id from data_landuse.ca_tmp_landuse_type_tbl t
join data_landuse.ca_landuse_type_tbl p on st_overlaps(t.geometry, p.geometry)
where t.parcel_id = 8


CREATE OR REPLACE FUNCTION base.calculate_set_plan_zone_relation(tmp_parcel_id integer)
    RETURNS TABLE(parcel_id integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE 
    ROWS 1000
AS $BODY$

DECLARE
	v_utmsrid integer;
BEGIN
    
	RETURN  query select p.parcel_id from data_landuse.ca_tmp_landuse_type_tbl t
			join data_landuse.ca_landuse_type_tbl p on st_overlaps(t.geometry, p.geometry)
			where t.parcel_id = tmp_parcel_id;

END;

$BODY$;

ALTER FUNCTION base.calculate_set_plan_zone_relation(integer)
    OWNER TO geodb_admin;

select base.calculate_set_plan_zone_relation(8)

