CREATE OR REPLACE FUNCTION base.gn_get_parcel_geo_id(IN input_polgyon_geometry geometry)
  RETURNS TABLE(geo_id text) AS
$BODY$

DECLARE
	spa_count integer;
	v_utmsrid integer;
BEGIN 
    
	IF (input_polgyon_geometry is null) THEN
	  RAISE exception '%', 'Polygon Geometry is null!';
	END IF;

	IF NOT(st_geometrytype(input_polgyon_geometry) = 'ST_Polygon' OR st_geometrytype(input_polgyon_geometry) = 'ST_MultiPolygon') THEN
		RAISE exception '%', 'Wrong geometry type. Only polygon';
	END IF;

	SELECT base.find_utm_srid(st_centroid(input_polgyon_geometry)) into v_utmsrid;
	IF NOT FOUND THEN
	  RAISE EXCEPTION '%','SRID not found';
	END IF;

	RETURN query select b.geo_id::text
			from 
			(select input_polgyon_geometry as geometry) a, 
			data_address_import.gn_soft b
			group by b.geo_id, b.documentname, b.geo_data
			order by min(st_distance(a.geometry, b.geo_data)) limit 1;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.gn_get_parcel_geo_id(geometry)
  OWNER TO geodb_admin;