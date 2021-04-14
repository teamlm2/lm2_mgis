-- Function: base.st_auto_street_select(integer, integer)

-- DROP FUNCTION base.st_auto_street_select(integer, integer);

CREATE OR REPLACE FUNCTION base.st_auto_street_select(
    str_calc_count integer,
    str_select_count integer,    
    parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	str_id integer;
BEGIN

execute 'select str_id from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line, 
	st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) 
	from (select * from data_address.st_entrance where parcel_id = $3 limit 1) e, data_address.st_street s 
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = $3
	order by st_distance(a.geometry, s.line_geom) asc
	limit $1)
	group by entrance_id, id, e.geometry
	order by min(st_distance(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry)) asc)sss
	where str_id not in
	(select str_id from (
	select entrance_id, s.id as str_id, st_makeline(ST_ClosestPoint(s.line_geom, e.geometry), e.geometry) as st_line 
	from (select * from data_address.st_entrance where parcel_id = $3 limit 1) e, data_address.st_street s
	where s.id in (select s.id from data_address.ca_parcel_address a, data_address.st_street s
	where a.id = $3
	order by st_distance(a.geometry, s.line_geom) asc
	limit $1)) a ,
	(select id, st_makeline(sp, ep) as p_boundary from (
	select id, ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
	ST_PointN(geom, generate_series(2, ST_NPoints(geom) )) as ep from (
	select id, st_geometrytype(geometry), st_geometrytype(st_boundary(geometry)), (st_boundary(geometry)) as geom from data_address.ca_parcel_address
	where id = $3
	)xxx
	)ccc) b
	where st_crosses(st_line, p_boundary))
	limit $2 ' into str_id USING str_calc_count, str_select_count, parcel_id;

return str_id;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_auto_street_select(integer, integer, integer)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select(integer, integer, integer) TO public;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select(integer, integer, integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_auto_street_select(integer, integer, integer) TO application_update;

select base.st_auto_street_select(10, 10, 795369)