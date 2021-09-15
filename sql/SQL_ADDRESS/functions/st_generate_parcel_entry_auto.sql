-- Function: base.st_generate_parcel_entry_auto(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_generate_parcel_entry_auto(integer);
DROP FUNCTION if exists base.st_generate_parcel_entry_auto(integer);

CREATE OR REPLACE FUNCTION base.st_generate_parcel_entry_auto(
    IN p_id integer)
  RETURNS TABLE(entry_type int, x float, y float) AS
$BODY$

DECLARE
	v_utmsrid integer;
BEGIN

	    RETURN  query 
			select 1, ST_X(xxx.geom) as xx, ST_Y(xxx.geom) as yy from (
			select xxx.* from (
			SELECT row_number() over() gid, st_centroid(line.geom) as geom
			FROM ST_Boundary(((select ((geometry)) from data_address.ca_parcel_address where id = p_id))) AS t(geom)
			CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(xs)
			CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, xs), ST_PointN(geom, xs+1)) AS line(geom)
			)xxx
			where gid not in ( 
			select aa.gid from (
			SELECT row_number() over() gid, ST_SRID(line.geom) ,st_centroid(line.geom) as geom
			FROM ST_Boundary(((select ((geometry)) from data_address.ca_parcel_address where id = p_id))) AS t(geom)
			CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(xa)
			CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, xa), ST_PointN(geom, xa+1)) AS line(geom)
			) aa, (select p.parcel_id, d.parcel_id, d.geometry from data_address.ca_parcel_address p, data_address.ca_parcel_address d where p.id = p_id and st_touches(p.geometry, d.geometry) and now() between d.valid_from and d.valid_till) p
			where st_intersects((aa.geom),(st_buffer(p.geometry, 0.000001)))) 
			)xxx, data_address.st_all_street_line_view line
			group by xxx.gid, xxx.geom
			order by min(st_distance(line.geometry, xxx.geom)) asc limit 1;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_generate_parcel_entry_auto(str_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_generate_parcel_entry_auto(id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_generate_parcel_entry_auto(integer) TO application_update;
