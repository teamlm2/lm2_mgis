-- Function: base.st_street_line_view_start_end_nodes_auto(integer)

-- DROP FUNCTION base.st_street_line_view_start_end_nodes_auto(integer);

CREATE OR REPLACE FUNCTION base.st_street_line_view_start_end_nodes_auto(IN str_id integer)
  RETURNS TABLE(gid integer, street_id bigint, x double precision, y double precision, dist double precision) AS
$BODY$

DECLARE
	ub_str_count integer;
BEGIN		
		EXECUTE 'select count(au2) from data_address.st_street s where s.id = ''' || str_id || ''' and au2 in (''01107'', ''01110'', ''01116'', ''01119'', ''01122'', ''01125'');' INTO ub_str_count;
		RAISE NOTICE 'ub_str_count (%)',  ub_str_count;	
		IF (ub_str_count = 0) THEN
		  	--RAISE NOTICE 'str_id 1 (%)',  str_id;		
			RETURN  query 
				select * from (
				select 1 as gid, xxx.id as street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, min(st_distance(xxx.geom, sp.geometry)) as dist from (
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
				order by st_distance(xxx.geom, sp.geometry) asc limit 1
				)xxx
				union all 
				select * from (
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
				order by st_distance(xxx.geom, sp.geometry) desc limit 1
				)xxx;
		ELSE
			--RAISE NOTICE 'str_id 2 (%)',  str_id;
			RETURN  query 
				select * from (
				select 1 as gid, xxx.id as street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, min(st_distance(xxx.geom, sp.geometry)) as dist from (
				select count(geom) as cc, id, geom, line_geom from (
				select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				union all
				select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				)sss 
				group by geom, line_geom, id
				)xxx, (select sp.* from data_address.au_settlement_zone_point sp, admin_units.au_level2 au2 where st_within(sp.geometry, au2.geometry) and au2.code in ('01107', '01110', '01116', '01119', '01122', '01125')) sp 
				where cc = 1
				group by xxx.id, xxx.geom, xxx.line_geom, xxx.cc, sp.geometry
				order by st_distance(xxx.geom, sp.geometry) asc limit 1
				)xxx
				union all
				select * from (
				select 2 as gid, xxx.id as street_id, ST_X(xxx.geom) as x, ST_Y(xxx.geom) as y, min(st_distance(xxx.geom, sp.geometry)) as dist from (
				select count(geom) as cc, id, geom, line_geom from (
				select s.id, ST_StartPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				union all
				select s.id, ST_EndPoint((ST_Dump(line_geom)).geom) as geom, s.au2, s.line_geom from data_address.st_street s where s.id = str_id
				)sss 
				group by geom, line_geom, id
				)xxx, (select sp.* from data_address.au_settlement_zone_point sp, admin_units.au_level2 au2 where st_within(sp.geometry, au2.geometry) and au2.code in ('01107', '01110', '01116', '01119', '01122', '01125')) sp 
				where cc = 1
				group by xxx.id, xxx.geom, xxx.line_geom, xxx.cc, sp.geometry
				order by st_distance(xxx.geom, sp.geometry) desc limit 1
				)xxx;
		END IF;
			
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
