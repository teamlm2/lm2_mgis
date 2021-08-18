-- Function: base.st_street_line_view_start_end_points(integer)

-- DROP FUNCTION base.st_street_line_view_start_end_points(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_points(IN str_id integer)
  RETURNS TABLE(gid integer, street_id bigint, x double precision, y double precision, dist double precision) AS
$BODY$

DECLARE
	ub_str_count integer;
BEGIN		
		RETURN  query 
			select 2 as gid, xxx.id as street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, min(st_distance(xxx.geom, sp.geometry)) as dist from (
			select count(geom) as cc, id, geom, line_geom from (
			select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
			union all
			select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
			)sss 
			group by geom, line_geom, id
			)xxx, (select sp.* from (
				select count(geom) as cc, id, geom, line_geom from (
				select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				union all
				select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				)sss 
				group by geom, line_geom, id
				)xxx, data_address.au_settlement_zone_point sp 
				where xxx.cc = 1
				order by st_distance(xxx.geom, sp.geometry) asc limit 1) sp 
			where cc = 1
			group by xxx.id, xxx.geom, xxx.line_geom, xxx.cc, sp.geometry
			order by st_distance(xxx.geom, sp.geometry) asc;
			
END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_street_line_view_start_end_points(integer)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_points(integer) TO public;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_points(integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_view_start_end_points(integer) TO application_update;
