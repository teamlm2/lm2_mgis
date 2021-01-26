-- Function: base.st_street_line_view_start_end_nodes_auto(integer)

-- DROP FUNCTION base.st_street_line_view_start_end_nodes_auto(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_nodes_auto(IN str_id integer)
  RETURNS TABLE(gid integer, street_id bigint, x double precision, y double precision, dist double precision) AS
$BODY$

DECLARE
	v_utmsrid integer;
BEGIN

	    RETURN  query 
			select * from (
			select 1 as gid, xxx.id street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, min(st_distance(xxx.geom, sp.geometry)) as dist from data_address.au_settlement_zone_point sp , 
			(select * from (
			select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom from data_address.st_street s where s.id = str_id
			union all
			select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom from data_address.st_street s where s.id = str_id
			)xxx group by id, geom)xxx
			group by xxx.id, xxx.geom
			order by min(st_distance(xxx.geom, sp.geometry)) asc limit 1)xxx
			union all
			select * from (
			select 2 as gid, xxx.id street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, max(st_distance(xxx.geom, sp.geometry)) as dist from data_address.au_settlement_zone_point sp , 
			(select * from (
			select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom from data_address.st_street s where s.id = str_id
			union all
			select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom from data_address.st_street s where s.id = str_id
			)xxx group by id, geom)xxx
			group by xxx.id, xxx.geom
			order by max(st_distance(xxx.geom, sp.geometry)) asc limit 1)xxx;

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

select * from base.st_street_line_view_start_end_nodes_auto(136194)