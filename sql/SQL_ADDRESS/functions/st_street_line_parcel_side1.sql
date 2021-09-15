-- Function: base.st_street_line_parcel_side1(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_street_line_parcel_side1(integer, geometry, geometry, geometry, integer);
DROP FUNCTION if exists base.st_street_line_parcel_side1(integer, integer);

CREATE OR REPLACE FUNCTION base.st_street_line_parcel_side1(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	side_value integer;
BEGIN

execute 'select
case
	when degrees(ST_Azimuth(st_centroid(h.vec), st_centroid(h.seg))) > 180 then 1 
	else -1
end as side
from (
    select 
        ST_MakeLine(cp.p, st_centroid(point.geometry)) vec,
        ST_MakeLine(cp.p, 
            ST_LineInterpolatePoint(
                ST_LineMerge(((line.geometry))), 
                ST_LineLocatePoint(ST_LineMerge(((line.geometry))), cp.p) * 1.01) 
        ) seg
        from (
            select ST_ClosestPoint(line.geometry, st_centroid(point.geometry)) as p from data_address.ca_parcel_address point, data_address.st_all_street_line_view line where line.id = $1 and point.id = $2
        )cp, data_address.ca_parcel_address point, (select line.geometry, line.id from (
select 
ST_LineMerge((st_dump(line.geometry)).geom) as geometry, line.id
from data_address.st_all_street_line_view line where line.id = $1
) line, data_address.ca_parcel_address point where point.id = $2
group by line.geometry, line.id
order by min(st_distance(line.geometry, point.geometry)) asc limit 1) line where line.id = $1 and point.id = $2
    ) as h ' into side_value USING str_id, parcel_id;

return side_value;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_line_parcel_side1(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_street_line_parcel_side1(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_line_parcel_side1(integer, integer) TO application_update;

select unnest(string_to_array(base.st_street_line_parcel_side1(56436, 427340)::text, ','));
