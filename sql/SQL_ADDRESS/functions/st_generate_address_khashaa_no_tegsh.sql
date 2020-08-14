-- Function: base.st_generate_address_khashaa_no_tegsh(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_generate_address_khashaa_no_tegsh(integer, integer);
DROP FUNCTION if exists base.st_generate_address_khashaa_no_tegsh(integer, integer);

CREATE OR REPLACE FUNCTION base.st_generate_address_khashaa_no_tegsh(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	st_generate_address_khashaa_no_tegsh integer;
BEGIN

execute 'select 
case 
	when p.p_n = ''0'' and (select unnest(string_to_array(base.st_street_parcel_side_with_str_start_point($1, $2)::text, '',''))) = ''1'' then s.start_number + 2	
	else p.p_n::int + 2
end as parcel_address_no
 from (
select COALESCE(max(address_parcel_no)::text, ''0'') as p_n from data_address.ca_parcel_address p
where p.address_parcel_no ~ ''^[0-9]'' and p.street_id = $1 and (p.address_parcel_no::int % 2) = 0
)p , data_address.st_street s
where s.id = $1 ' into st_generate_address_khashaa_no_tegsh USING str_id, parcel_id;

return st_generate_address_khashaa_no_tegsh;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_generate_address_khashaa_no_tegsh(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_generate_address_khashaa_no_tegsh(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_generate_address_khashaa_no_tegsh(integer, integer) TO application_update;

select unnest(string_to_array(base.st_generate_address_khashaa_no_tegsh(56442, 427182)::text, ','));
