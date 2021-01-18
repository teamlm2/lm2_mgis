-- Function: base.st_street_line_view_start_end_nodes(integer)

-- DROP FUNCTION base.st_street_line_view_start_end_nodes(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_nodes(IN str_id integer)
  RETURNS TABLE(id bigint, street_id bigint, x double precision, y double precision) AS
$BODY$

DECLARE
	v_utmsrid integer;
BEGIN

	    RETURN  query 
			SELECT row_number() over() as gid, * FROM (
			select  s.street_id, ST_X(ST_StartPoint((ST_Dump(geometry)).geom)) as x, ST_Y(ST_StartPoint((ST_Dump(geometry)).geom)) as y from data_address.st_mat_street_line_view s where s.street_id = 128888
			union all
			select  s.street_id, ST_X(ST_EndPoint((ST_Dump(geometry)).geom)) as x, ST_Y(ST_EndPoint((ST_Dump(geometry)).geom)) as y from data_address.st_mat_street_line_view s where s.street_id = 128888
)XXX group by xxx.street_id, xxx.x, xxx.y

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_street_line_view_start_end_nodes(integer)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes(integer) TO public;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes(integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes(integer) TO application_update;

select * from base.st_street_line_view_start_end_nodes(128888)


SELECT foo.gid, ST_StartPoint(the_geom) as geom
			FROM (select s.street_id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from data_address.st_mat_street_line_view s where s.street_id = str_id

select ST_StartPoint((ST_Dump(geometry)).geom) from data_address.st_mat_street_line_view where street_id = 128888

select ST_EndPoint((ST_Dump(geometry)).geom) from data_address.st_mat_street_line_view where street_id = 128888

select * from (
SELECT foo.gid, ST_StartPoint(the_geom) as geom
FROM (select s.street_id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from data_address.st_mat_street_line_view s where s.street_id = 128888) As foo
union all
SELECT foo.gid, ST_EndPoint(the_geom) as geom
FROM (select s.street_id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from data_address.st_mat_street_line_view s where s.street_id = 128888) As foo
)xxx group by gid, geom
