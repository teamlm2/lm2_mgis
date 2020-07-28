-- Function: base.st_street_line_view_start_end_nodes(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_street_line_view_start_end_nodes(integer, geometry, geometry, geometry, integer);
DROP FUNCTION if exists base.st_street_line_view_start_end_nodes(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_nodes(
    IN str_id integer)
  RETURNS TABLE(id bigint, street_id bigint, x float, y float) AS
$BODY$

DECLARE
	v_utmsrid integer;
BEGIN

	    RETURN  query 
			select row_number() over() as gid, xxx.gid as street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y from (
			SELECT foo.gid, ST_StartPoint(the_geom) as geom
			FROM (select xxx.id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from 
				  (
					SELECT s.id,
			    s.code,
			    s.name,
			    s.description,
			    s.decision_date,
			    s.decision_no,
			    s.decision_level_id,
			    dl.description AS decision_level_desc,
			    s.is_active,
			    s.street_type_id,
			    s.length,
			    r.geometry::geometry(MultiLineString,4326) AS geometry
			   FROM data_address.st_street s
			     LEFT JOIN data_plan.cl_plan_decision_level dl ON s.decision_level_id = dl.plan_decision_level_id
			     JOIN ( SELECT row_number() OVER () AS gid,
				    st_union(st_multi(st_road.line_geom)) AS geometry,
				    st_road.street_id
				   FROM data_address.st_road
				  WHERE st_road.street_id IS NOT NULL
				  GROUP BY st_road.street_id) r ON s.id = r.street_id where s.id = str_id
				  )xxx
			where xxx.id = str_id) As foo
			union all
			SELECT foo.gid, ST_EndPoint(the_geom) as geom
			FROM (select xxx.id as gid, (ST_Dump(geometry)).geom As the_geom, geometry from 
				  (
					SELECT s.id,
			    s.code,
			    s.name,
			    s.description,
			    s.decision_date,
			    s.decision_no,
			    s.decision_level_id,
			    dl.description AS decision_level_desc,
			    s.is_active,
			    s.street_type_id,
			    s.length,
			    r.geometry::geometry(MultiLineString,4326) AS geometry
			   FROM data_address.st_street s
			     LEFT JOIN data_plan.cl_plan_decision_level dl ON s.decision_level_id = dl.plan_decision_level_id
			     JOIN ( SELECT row_number() OVER () AS gid,
				    st_union(st_multi(st_road.line_geom)) AS geometry,
				    st_road.street_id
				   FROM data_address.st_road
				  WHERE st_road.street_id IS NOT NULL
				  GROUP BY st_road.street_id) r ON s.id = r.street_id where s.id = str_id
				  )xxx
			where xxx.id = str_id) As foo
			)xxx group by xxx.gid, xxx.geom;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_street_line_view_start_end_nodes(str_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes(id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_nodes(integer) TO application_update;
