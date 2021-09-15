-- Function: base.st_auto_street_select_au2(integer, integer, bigint)

-- DROP FUNCTION base.st_auto_street_select_au2(integer, integer, bigint);

CREATE OR REPLACE FUNCTION base.st_auto_street_select_au2(
    IN str_calc_count integer,
    IN str_select_count integer,
    IN in_parcel_id bigint)
  RETURNS TABLE(str_id bigint) AS
$BODY$

DECLARE
	p_str_id integer;
BEGIN

RETURN query select sss.str_id::bigint from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line, 
	st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) 
	from (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) e, (select id, st_multi(st_union(xxx.line_geom))::geometry(MultiLineString,4326) AS line_geom from (
select street_id as id , sr.line_geom from data_address.st_road sr 
where sr.street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
union all 
select belong_street_id as id , sr.line_geom from data_address.st_road sr 
where sr.belong_street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
		)xxx
group by id) s 
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = in_parcel_id
	order by st_distance(a.geometry, s.line_geom) asc
	limit str_calc_count)
	group by entrance_id, id, e.geometry, s.line_geom
	order by min(st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry)) asc)sss
	where sss.str_id not in
	(select a.str_id from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line 
	from (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) e, (select id, st_multi(st_union(xxx.line_geom))::geometry(MultiLineString,4326) AS line_geom from (
select street_id as id , sr.line_geom from data_address.st_road sr 
where sr.street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
union all 
select belong_street_id as id , sr.line_geom from data_address.st_road sr 
where sr.belong_street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
		)xxx
group by id) s
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = in_parcel_id
	order by st_distance(a.geometry, s.line_geom) asc
	limit str_calc_count)) a ,
	(select ddd.* from (
	select id, st_makeline(sp, ep) as p_boundary from (
	select id, ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
	ST_PointN(geom, generate_series(2, ST_NPoints(geom) )) as ep from (
	select id, st_geometrytype(geometry), st_geometrytype(st_boundary(geometry)), (st_boundary(geometry)) as geom from data_address.ca_parcel_address
	where id = in_parcel_id
	)xxx
	)ccc
	)ddd, (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) aaa
	where not ST_DWithin(aaa.geometry, ddd.p_boundary, 0.00001)) b
	where st_crosses(st_line, p_boundary))
	union all
	select sss.str_id::bigint from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line, 
	st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) 
	from (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) e, (select id, st_multi(st_union(xxx.line_geom))::geometry(MultiLineString,4326) AS line_geom from (
select street_id as id , sr.line_geom from data_address.st_road sr 
where sr.street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
union all 
select belong_street_id as id , sr.line_geom from data_address.st_road sr 
where sr.belong_street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
		)xxx
group by id) s 
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = in_parcel_id
	order by st_distance(a.geometry, s.line_geom) asc
	limit str_calc_count)
	group by entrance_id, id, e.geometry, s.line_geom
	order by min(st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry)) asc)sss
	where sss.str_id in
	(select a.str_id from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line 
	from (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) e, (select id, st_multi(st_union(xxx.line_geom))::geometry(MultiLineString,4326) AS line_geom from (
select street_id as id , sr.line_geom from data_address.st_road sr 
where sr.street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
union all 
select belong_street_id as id , sr.line_geom from data_address.st_road sr 
where sr.belong_street_id in (
select s.id from data_address.ca_parcel_address a, data_address.st_street s
		where a.id = in_parcel_id
		order by st_distance(a.geometry, s.line_geom) asc
		limit str_calc_count)
		)xxx
group by id) s
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = in_parcel_id
	order by st_distance(a.geometry, s.line_geom) asc
	limit str_calc_count)) a ,
	(select ddd.* from (
	select id, st_makeline(sp, ep) as p_boundary from (
	select id, ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
	ST_PointN(geom, generate_series(2, ST_NPoints(geom) )) as ep from (
	select id, st_geometrytype(geometry), st_geometrytype(st_boundary(geometry)), (st_boundary(geometry)) as geom from data_address.ca_parcel_address
	where id = in_parcel_id
	)xxx
	)ccc
	)ddd, (select * from data_address.st_entrance where parcel_id = in_parcel_id limit 1) aaa
	where not ST_DWithin(aaa.geometry, ddd.p_boundary, 0.00001)) b
	where st_crosses(st_line, p_boundary))
	limit str_select_count;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.st_auto_street_select_au2(integer, integer, bigint)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select_au2(integer, integer, bigint) TO public;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select_au2(integer, integer, bigint) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select_au2(integer, integer, bigint) TO application_update;
