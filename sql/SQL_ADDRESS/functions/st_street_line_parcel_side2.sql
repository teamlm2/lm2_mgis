start_line_x start_line_y
entry_intersects_x entry_intersects_y
end_line_x end_line_y
entry_point_x entry_point_y

str_id
parcel_id


SELECT
	ST_LineCrossingDirection(foo.line1, foo.line2) As l1_cross_l2 --,
	--ST_LineCrossingDirection(foo.line2, foo.line1) As l2_cross_l1
FROM (
 SELECT
  ST_GeomFromText('LINESTRING(start_line_x start_line_y, entry_intersects_x entry_intersects_y, end_line_x end_line_y)') As line2,
  ST_GeomFromText('LINESTRING(start_line_x start_line_y, entry_intersects_x entry_intersects_y, entry_point_x entry_point_y)') As line1
  ) As foo;

----------
------------
SELECT
	ST_LineCrossingDirection(foo.line1, foo.line2) As l1_cross_l2 --,
	--ST_LineCrossingDirection(foo.line2, foo.line1) As l2_cross_l1
FROM (
 SELECT
  ST_GeomFromText('LINESTRING(108.416787158867 46.3358094239678, 108.41678715972 46.3393020080482, 108.417721727751 46.3410167363241)') As line2,
  ST_GeomFromText('LINESTRING(108.416787158867 46.3358094239678, 108.41678715972 46.3393020080482, 108.418717939009 46.3381773504626)') As line1
  ) As foo;


select geometry from data_address.st_entrance where parcel_id = 846699;
select geometry as line_geom from data_address.st_all_street_line_view where id = 62978;

select * from data_address.st_street_point where street_id = 62978;
select geometry from data_address.st_street_point where street_id = 62978 and point_type = 1;
----------------

-- DROP FUNCTION base.st_street_line_parcel_side2(integer, integer);
DROP FUNCTION if exists base.st_street_line_parcel_side2(integer, integer);

CREATE OR REPLACE FUNCTION base.st_street_line_parcel_side2(
    IN str_id integer, parcel_id integer)
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
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and type = 1 limit 1) point_1
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
 SELECT st_intersection(cp.vec, cp.line) as intersect_point FROM cp; ' into intersection_point USING str_id, parcel_id;

execute 'WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and type = 1 limit 1) point_1
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
 SELECT st_x(st_intersection(cp.vec, cp.line)) as intersect_point FROM cp; ' into intersection_point_x USING str_id, parcel_id;

execute 'WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = $2 and type = 1 limit 1) point_1
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
 SELECT st_y(st_intersection(cp.vec, cp.line)) as intersect_point FROM cp; ' into intersection_point_y USING str_id, parcel_id;

aaa := 'LINESTRING(' ||(start_point_x)::text || ' ' || (start_point_y)::text ||','|| (intersection_point_x)::text || ' ' ||  (intersection_point_y)::text ||','|| (end_point_x)::text || ' ' || (end_point_y)::text || ')';
bbb := 'LINESTRING(' ||(start_point_x)::text || ' ' || (start_point_y)::text ||','|| (intersection_point_x)::text || ' ' ||  (intersection_point_y)::text ||','|| (entry_point_x)::text || ' ' || (entry_point_y)::text || ')';

execute 'SELECT
	ST_LineCrossingDirection(foo.line2, foo.line1) As l1_cross_l2
	FROM (
	 SELECT
	  ST_GeomFromText('''||aaa||''') As line2,
	  ST_GeomFromText('''||bbb||''') As line1
	  ) As foo;' into st_street_line_parcel_side2;



return st_street_line_parcel_side2;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_line_parcel_side2(str_id integer, parcel_id integer) OWNER TO geodb_admin;

select unnest(string_to_array(base.st_street_line_parcel_side2(58794, 1293342)::text, ','));


-----------------

select xxx.aa from (
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
order by min(st_distance(bbb.geometry, xxx.aa)) desc limit 1
 
 ------------------
 
 --entry
select geometry from data_address.st_entrance where parcel_id = 1528255 order by type asc limit 1;
select geometry from data_address.st_entrance where parcel_id = 1528255 and type = 1 limit 1; 
--start
select geometry from data_address.st_street_point where street_id = 58794 and point_type = 1;

--end
select geometry from data_address.st_street_point where street_id = 58794 and point_type = 2 limit 1;








