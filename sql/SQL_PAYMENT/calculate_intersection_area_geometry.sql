
DROP FUNCTION if exists base.calculate_intersection_area_geometry(in geometry(Polygon,4326), geometry(Polygon,4326), integer);

-- /input_zone_id, input_geometry/
CREATE OR REPLACE FUNCTION base.calculate_intersection_area_geometry(IN
    intersection_geom1 geometry(Polygon,4326),
    intersection_geom2 geometry(Polygon,4326),
    round_value integer)
  RETURNS numeric AS 
$BODY$

DECLARE
        pol geometry(Polygon,4326);
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


execute 'select round(st_area(st_intersection(ST_Transform($1, base.find_utm_srid(st_centroid($1))), ST_Transform($2, base.find_utm_srid(st_centroid($1)))))::numeric, $3) ' into area_m2 USING intersection_geom1, intersection_geom2, round_value;

    return area_m2;
END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.calculate_intersection_area_geometry(geometry(Polygon,4326), geometry(Polygon,4326), integer)
  OWNER TO geodb_admin;
--------------
