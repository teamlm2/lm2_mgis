DROP FUNCTION base.calculate_distance_cama_parcel(integer, text);

CREATE OR REPLACE FUNCTION base.calculate_distance_cama_parcel(
    cama_landuse integer,
    parcel_id text)
  RETURNS text[] AS
$BODY$

DECLARE
    
    distance text;
    geometry geometry(Polygon,4326);
    v_utmsrid integer;
    id text;
    value_array text array;
BEGIN
    IF (parcel_id is  null) THEN
      RAISE exception '%', 'parcel id is null!';
    END IF;
    
    EXECUTE 'select geometry from data_soums_union.ca_parcel_tbl where parcel_id = ''' || parcel_id || ''';' INTO geometry;     /* have tried selecting  as well */
    
    IF (geometry is  null) THEN
      RAISE exception '%', 'Geometry is null!';
    END IF;

    IF NOT(st_geometrytype(geometry) = 'ST_Polygon' OR st_geometrytype(geometry) = 'ST_MultiPolygon') THEN
      RAISE exception '%', 'Wrong geometry type';
    END IF;

    SELECT base.find_utm_srid(st_centroid(geometry)) into v_utmsrid;
    IF NOT FOUND THEN
      RAISE EXCEPTION '%','SRID not found';
    END IF;

    EXECUTE 'SELECT array[round(ST_Distance(ST_Transform(a.geometry, '|| v_utmsrid ||'), ST_Transform(b.geometry, '|| v_utmsrid ||'))::numeric, 2)::text, b.id::text]
	FROM data_soums_union.ca_parcel_tbl a, data_cama.cm_parcel_tbl b 
	WHERE a.parcel_id = '''|| parcel_id ||''' and b.cama_landuse = '|| cama_landuse ||' 
	ORDER BY ST_Distance(a.geometry, b.geometry) LIMIT 1;' INTO value_array;

    RETURN value_array;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.calculate_distance_cama_parcel(integer, text)
  OWNER TO geodb_admin;
--------------


select base.calculate_distance_cama_parcel(320301, '1160800002');