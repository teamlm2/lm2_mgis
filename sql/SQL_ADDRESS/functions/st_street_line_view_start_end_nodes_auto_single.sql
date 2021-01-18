-- Function: base.st_street_line_view_start_end_nodes_auto(integer)

-- DROP FUNCTION base.st_street_line_view_start_end_nodes_auto(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_nodes_auto(IN str_id integer)
  RETURNS TABLE(gid bigint, street_id bigint, x double precision, y double precision, dist double precision) AS
$BODY$

DECLARE
	v_utmsrid integer;
BEGIN

	    RETURN  query 
			select row_number() over() as gid , xxx.* from (
			select xxx.street_id, ST_X(xxx.geometry) as x, ST_Y(xxx.geometry) as y, min(st_distance(xxx.geometry, sss.geometry)) from (
			select s.id, sp.geometry from data_address.st_all_street_line_view s, data_address.au_settlement_zone_point sp
			where s.id = str_id group by s.id, sp.id order by min(st_distance(s.geometry, sp.geometry)) asc limit 1
			)sss,
			(select row_number() over() as gid, xxx.gid as street_id, xxx.geom geometry, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y from (

			SELECT foo.gid, ST_StartPoint(the_geom) as geom
			FROM (select s.street_id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from data_address.st_mat_street_line_view s where s.street_id = str_id) As foo

			)xxx group by xxx.gid, xxx.geom)xxx group by xxx.street_id, xxx.geometry order by min(st_distance(xxx.geometry, sss.geometry)) asc)xxx;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_street_line_view_start_end_nodes_auto(integer)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes_auto(integer) TO public;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes_auto(integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes_auto(integer) TO application_update;
