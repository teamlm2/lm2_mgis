
DROP FUNCTION if exists base.calculate_intersection_transform_geometry(in geometry(Polygon,4326), geometry(Polygon,4326));

-- /input_zone_id, input_geometry/
CREATE OR REPLACE FUNCTION base.calculate_intersection_transform_geometry(IN
    intersection_geom1 geometry(Polygon,4326),
    intersection_geom2 geometry(Polygon,4326))
  RETURNS geometry AS 
$BODY$

DECLARE
        intersection_polygon geometry;
	v_utmsrid integer;
        is_cadastre_count integer;
	overlaps_parcel_count integer;
        area_m2 numeric;        
BEGIN
    IF (intersection_geom1 is null) THEN
      RAISE exception '%', 'geometry 1 is null!';
    END IF; 

    SELECT base.find_utm_srid(st_centroid(intersection_geom1)) into v_utmsrid;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'intersection_geom1 %','SRID not found';
    END IF;

    SELECT base.find_utm_srid(st_centroid(intersection_geom2)) into v_utmsrid;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'intersection_geom2 %','SRID not found';
    END IF;


execute 'select st_intersection(ST_Transform($1, base.find_utm_srid(st_centroid($1))), ST_Transform($2, base.find_utm_srid(st_centroid($1)))) ' into intersection_polygon USING intersection_geom1, intersection_geom2;

    return intersection_polygon;
END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.calculate_intersection_transform_geometry(geometry(Polygon,4326), geometry(Polygon,4326))
  OWNER TO geodb_admin;
--------------
