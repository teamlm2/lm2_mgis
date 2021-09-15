-- Function: base.st_generate_address_khashaa_no(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.st_generate_address_khashaa_no(integer, integer);
DROP FUNCTION if exists base.st_generate_address_khashaa_no(integer, integer);

CREATE OR REPLACE FUNCTION base.st_generate_address_khashaa_no(
    IN str_id integer, parcel_id integer)
  RETURNS integer AS
$BODY$

DECLARE
	st_generate_address_khashaa_no integer;
BEGIN

execute 'select 
case 
	when p.p_n = ''0'' and (select unnest(string_to_array(base.st_street_parcel_side_with_str_start_point($1, $2)::text, '',''))) = ''-1'' then s.start_number + 1
	when p.p_n = ''0'' and (select unnest(string_to_array(base.st_street_parcel_side_with_str_start_point($1, $2)::text, '',''))) = ''1'' then s.start_number + 2	
	else p.p_n::int + 2
end as parcel_address_no
 from (
select COALESCE(max(address_parcel_no)::text, ''0'') as p_n from data_address.ca_parcel_address p
where p.address_parcel_no ~ ''^[0-9]'' and p.street_id = $1
)p , data_address.st_street s
where s.id = $1 ' into st_generate_address_khashaa_no USING str_id, parcel_id;

return st_generate_address_khashaa_no;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_generate_address_khashaa_no(str_id integer, parcel_id integer)
  OWNER TO geodb_admin;

GRANT EXECUTE ON FUNCTION base.st_generate_address_khashaa_no(str_id integer, parcel_id integer) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.st_generate_address_khashaa_no(integer, integer) TO application_update;

select unnest(string_to_array(base.st_generate_address_khashaa_no(56442, 427148)::text, ','));
