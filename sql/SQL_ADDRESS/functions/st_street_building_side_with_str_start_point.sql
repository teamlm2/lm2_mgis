-- Function: base.st_street_building_side_with_str_start_point(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_street_building_side_with_str_start_point(integer, integer);
DROP FUNCTION if exists base.st_street_building_side_with_str_start_point(integer, integer);

CREATE OR REPLACE FUNCTION base.st_street_building_side_with_str_start_point(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	side_value integer;
BEGIN

execute 'select * from (
select 
case 
	when degrees(ST_Azimuth(st_centroid(p.geometry), sp.geometry)) > 180 and (select unnest(string_to_array(base.st_street_line_building_side1($1, $2)::text, '','')))::int = 1 then 1
	when degrees(ST_Azimuth(st_centroid(p.geometry), sp.geometry)) > 180 and (select unnest(string_to_array(base.st_street_line_building_side1($1, $2)::text, '','')))::int = -1 then -1
	when degrees(ST_Azimuth(st_centroid(p.geometry), sp.geometry)) < 180 and (select unnest(string_to_array(base.st_street_line_building_side1($1, $2)::text, '','')))::int = -1 then 1
	when degrees(ST_Azimuth(st_centroid(p.geometry), sp.geometry)) < 180 and (select unnest(string_to_array(base.st_street_line_building_side1($1, $2)::text, '','')))::int = 1 then -1	
	else 0
end as side

from data_address.st_map_street_point ms, data_address.ca_building_address p, data_address.st_street_point sp

where ms.street_point_id = sp.id and ms.street_id = $1 and p.id = $2) as h ' into side_value USING str_id, parcel_id;

return side_value;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_building_side_with_str_start_point(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_street_building_side_with_str_start_point(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_street_building_side_with_str_start_point(integer, integer) TO application_update;

select unnest(string_to_array(base.st_street_building_side_with_str_start_point(62678, 1520959)::text, ','));
