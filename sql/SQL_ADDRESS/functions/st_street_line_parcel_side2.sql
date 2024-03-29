﻿-- Function: base.st_street_line_parcel_side2(bigint, bigint)

-- DROP FUNCTION base.st_street_line_parcel_side2(bigint, bigint);

CREATE OR REPLACE FUNCTION base.st_street_line_parcel_side2(
    str_id bigint,
    parcel_id bigint)
  RETURNS integer AS
$BODY$

DECLARE
	st_street_line_parcel_side2 integer;
    intersection_point geometry(Point,4326);
		
	start_point geometry(Point,4326);
	end_point geometry(Point,4326);
	entry_point geometry(Point,4326);

	intersection_point_x numeric;
	intersection_point_y numeric;
	
	start_point_x numeric;
	start_point_y numeric;
	
	end_point_x numeric;
	end_point_y numeric;
	
	entry_point_x numeric;
	entry_point_y numeric;
        aaa text;
	bbb text;
BEGIN
RAISE NOTICE 'parcel_id (%)',  parcel_id;
RAISE NOTICE 'str_id (%)',  str_id;
execute 'select geometry from data_address.st_entrance where parcel_id = $1 order by type asc limit 1; ' into entry_point USING parcel_id; 
execute 'select st_x(geometry) from data_address.st_entrance where parcel_id = $1 order by type asc limit 1; ' into entry_point_x USING parcel_id;
execute 'select st_y(geometry) from data_address.st_entrance where parcel_id = $1 order by type asc limit 1; ' into entry_point_y USING parcel_id;

execute 'select geometry from data_address.st_street_point where street_id = $1 and point_type = 1; ' into start_point USING str_id;
execute 'select st_x(geometry) from data_address.st_street_point where street_id = $1 and point_type = 1; ' into start_point_x USING str_id;
execute 'select st_y(geometry) from data_address.st_street_point where street_id = $1 and point_type = 1; ' into start_point_y USING str_id;

execute 'select xxx.aa as geometry from (
select xxx.aa from (
select ST_EndPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	)xxx
 union all
 select xxx.aa from (
select ST_StartPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	 )xxx
	)xxx,
 (select geometry from data_address.st_street_point where street_id = $1 and point_type = 1) bbb
 group by xxx.aa
order by min(st_distance(bbb.geometry, xxx.aa)) desc limit 1; ' into end_point USING str_id, parcel_id;

execute 'select st_x(xxx.aa) from (
select xxx.aa from (
select ST_EndPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	)xxx
 union all
 select xxx.aa from (
select ST_StartPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	 )xxx
	)xxx,
 (select geometry from data_address.st_street_point where street_id = $1 and point_type = 1) bbb
 group by xxx.aa
order by min(st_distance(bbb.geometry, xxx.aa)) desc limit 1; ' into end_point_x USING str_id, parcel_id;

execute 'select st_y(xxx.aa) from (
select xxx.aa from (
select ST_EndPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	)xxx
 union all
 select xxx.aa from (
select ST_StartPoint(s.line_geom) as aa from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1
	 )xxx
	)xxx,
 (select geometry from data_address.st_street_point where street_id = $1 and point_type = 1) bbb
 group by xxx.aa
order by min(st_distance(bbb.geometry, xxx.aa)) desc limit 1; ' into end_point_y USING str_id, parcel_id;

execute 'WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and is_active != FALSE limit 1) point_1
        ), street AS (SELECT line_1.line_geom AS geom FROM (select s.line_geom from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1) as line_1
        ), cp AS (SELECT a.gid AS ap_id, a.geom AS ap,
st_setsrid(st_addpoint(st_makeline(a.geom, st_closestpoint(b.geom, a.geom)), st_translate(a.geom, sin(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision, cos(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision)), 4326) AS vec,
st_setsrid(st_addpoint(st_linemerge(b.geom), st_translate(st_pointn(st_linemerge(b.geom), ''-2''::integer), sin(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision), cos(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision))), 4326) AS line
           FROM ap a
             LEFT JOIN street b ON st_dwithin(st_setsrid(b.geom, 4326), st_setsrid(a.geom, 4326), 25::double precision)
          ORDER BY a.gid, (st_distance(b.geom, a.geom))
        )
 SELECT (st_dump(st_intersection(cp.vec, cp.line))).geom as intersect_point FROM cp limit 1; ' into intersection_point USING str_id, parcel_id;

execute 'WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and is_active != FALSE limit 1) point_1
        ), street AS (SELECT line_1.line_geom AS geom FROM (select s.line_geom from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1) as line_1
        ), cp AS (SELECT a.gid AS ap_id, a.geom AS ap,
st_setsrid(st_addpoint(st_makeline(a.geom, st_closestpoint(b.geom, a.geom)), st_translate(a.geom, sin(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision, cos(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision)), 4326) AS vec,
st_setsrid(st_addpoint(st_linemerge(b.geom), st_translate(st_pointn(st_linemerge(b.geom), ''-2''::integer), sin(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision), cos(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision))), 4326) AS line
           FROM ap a
             LEFT JOIN street b ON st_dwithin(st_setsrid(b.geom, 4326), st_setsrid(a.geom, 4326), 25::double precision)
          ORDER BY a.gid, (st_distance(b.geom, a.geom))
        )
 SELECT st_x((st_dump(st_intersection(cp.vec, cp.line))).geom) as intersect_point FROM cp limit 1; ' into intersection_point_x USING str_id, parcel_id;

execute 'WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and is_active != FALSE limit 1) point_1
        ), street AS (SELECT line_1.line_geom AS geom FROM (select s.line_geom from data_address.st_entrance e,
 (select (st_dump(geometry)).geom as line_geom from data_address.st_all_street_line_view where id = $1) s
 where e.parcel_id = $2 group by s.line_geom order by min(st_distance(e.geometry, s.line_geom)) asc limit 1) as line_1
        ), cp AS (SELECT a.gid AS ap_id, a.geom AS ap,
st_setsrid(st_addpoint(st_makeline(a.geom, st_closestpoint(b.geom, a.geom)), st_translate(a.geom, sin(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision, cos(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision)), 4326) AS vec,
st_setsrid(st_addpoint(st_linemerge(b.geom), st_translate(st_pointn(st_linemerge(b.geom), ''-2''::integer), sin(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision), cos(st_azimuth(st_pointn(st_linemerge(b.geom), ''-2''::integer), st_pointn(st_linemerge(b.geom), ''-1''::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), ''-1''::integer), st_pointn(st_linemerge(b.geom), ''-2''::integer)) * 1.1::double precision))), 4326) AS line
           FROM ap a
             LEFT JOIN street b ON st_dwithin(st_setsrid(b.geom, 4326), st_setsrid(a.geom, 4326), 25::double precision)
          ORDER BY a.gid, (st_distance(b.geom, a.geom))
        )
 SELECT st_y((st_dump(st_intersection(cp.vec, cp.line))).geom) as intersect_point FROM cp limit 1; ' into intersection_point_y USING str_id, parcel_id;

aaa := 'LINESTRING(' ||(start_point_x)::text || ' ' || (start_point_y)::text ||','|| (intersection_point_x)::text || ' ' ||  (intersection_point_y)::text ||','|| (end_point_x)::text || ' ' || (end_point_y)::text || ')';


bbb := 'LINESTRING(' ||(start_point_x)::text || ' ' || (start_point_y)::text ||','|| (intersection_point_x)::text || ' ' ||  (intersection_point_y)::text ||','|| (entry_point_x)::text || ' ' || (entry_point_y)::text || ')';

RAISE NOTICE 'test x (%)',  intersection_point;
RAISE NOTICE 'test x (%)',  aaa;
RAISE NOTICE 'test y (%)',  bbb;
RAISE NOTICE 'ddddd (%)',  'select case when l1_cross_l2 in (1, -3, 2) then 1 else -1 end side from (
	SELECT
	ST_LineCrossingDirection(foo.line2, foo.line1) As l1_cross_l2
	FROM (
	 SELECT
	  --base.line_extend_straight('''||aaa||''') As line2,
st_setsrid(ST_GeomFromText('''||aaa||'''), 4326) As line2,	  
st_setsrid(ST_GeomFromText('''||bbb||'''), 4326) As line1
	  ) As foo)xxx;';

execute 'select case when l1_cross_l2 in (1, -3, 2) then 1 else -1 end side from (
	SELECT
	ST_LineCrossingDirection(foo.line2, foo.line1) As l1_cross_l2
	FROM (
	 SELECT
	  --base.line_extend_straight('''||aaa||''') As line2,
st_setsrid(ST_GeomFromText('''||aaa||'''), 4326) As line2,	  
st_setsrid(ST_GeomFromText('''||bbb||'''), 4326) As line1
	  ) As foo)xxx;' into st_street_line_parcel_side2;
return st_street_line_parcel_side2;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_line_parcel_side2(bigint, bigint)
  OWNER TO geodb_admin;
