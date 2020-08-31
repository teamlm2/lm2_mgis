-- Function: base.st_generate_address_building_without_parcel(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_generate_address_building_without_parcel(integer, integer);
DROP FUNCTION if exists base.st_generate_address_building_without_parcel(integer, integer);

CREATE OR REPLACE FUNCTION base.st_generate_address_building_without_parcel(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	st_generate_address_building_without_parcel integer;
BEGIN

execute 'select 
case 
	when p.p_n = ''0'' then COALESCE((s.building_start_number)::text, ''0'')::int + 1	
	else p.p_n::int + 1
end as parcel_address_no
 from (
select COALESCE(max(address_building_no)::text, ''0'') as p_n from data_address.ca_building_address p
where p.address_building_no ~ ''^[0-9]'' and p.street_id = $1
)p , data_address.st_street s
where s.id = $1 ' into st_generate_address_building_without_parcel USING str_id, parcel_id;

return st_generate_address_building_without_parcel;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_generate_address_building_without_parcel(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_generate_address_building_without_parcel(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_generate_address_building_without_parcel(integer, integer) TO application_update;

select unnest(string_to_array(base.st_generate_address_building_without_parcel(56442, 427182)::text, ','));
