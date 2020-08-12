-- Function: base.st_street_line_parcel_side(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_street_line_parcel_side(integer, geometry, geometry, geometry, integer);
DROP FUNCTION if exists base.st_street_line_parcel_side(integer, integer);

CREATE OR REPLACE FUNCTION base.st_street_line_parcel_side(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	side_value integer;
BEGIN

execute 'WITH ap AS (
				 SELECT point_1.id AS gid,
				    st_centroid(point_1.geometry) AS geom				 
				   FROM data_address.ca_parcel_address point_1 where  point_1.id = $1
				), street AS (
				 SELECT line_1.geometry AS geom
				   FROM data_address.st_all_street_line_view line_1
				  WHERE line_1.id = $2
				), cp AS (
				 SELECT a.gid AS id,
				    a.geom AS ap,				    
				    st_setsrid(st_addpoint(st_makeline(a.geom, st_closestpoint(b.geom, a.geom)), st_translate(a.geom, sin(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision, cos(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision)), 4326) AS vec,
				    st_setsrid(st_addpoint(st_linemerge(b.geom), st_translate(st_pointn(st_linemerge(b.geom), -2::integer), sin(st_azimuth(st_pointn(st_linemerge(b.geom), -2::integer), st_pointn(st_linemerge(b.geom), -1::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), -1::integer), st_pointn(st_linemerge(b.geom), -2::integer)) * 1.1::double precision), cos(st_azimuth(st_pointn(st_linemerge(b.geom), -2::integer), st_pointn(st_linemerge(b.geom), -1::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), -1::integer), st_pointn(st_linemerge(b.geom), -2::integer)) * 1.1::double precision))), 4326) AS line
				   FROM ap a
				     LEFT JOIN street b ON st_dwithin(st_setsrid(b.geom, 4326), st_setsrid(a.geom, 4326), 25::double precision)
				  ORDER BY a.gid, (st_distance(b.geom, a.geom))
				)
			 SELECT 
				st_linecrossingdirection(cp.line, cp.vec) AS side
			   FROM cp ' into side_value USING parcel_id, str_id;

return side_value;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_line_parcel_side(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_street_line_parcel_side(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_parcel_side(integer, integer) TO application_update;

select unnest(string_to_array(base.st_street_line_parcel_side(56442, 846588)::text, ','));
