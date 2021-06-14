CREATE OR REPLACE FUNCTION base.auto_numbering_odd_even(str_side numeric, parcel_count integer, find_id integer, start_number integer)
 RETURNS integer AS
$BODY$

DECLARE
    
    num integer;
   start_number_type numeric;
BEGIN  

execute 'select mod($1,2)' into start_number_type using start_number;

RAISE NOTICE 'test x (%)',  start_number_type;	

if str_side = -1 then
	if start_number_type::int <> 0 then
	    EXECUTE 'select num from (
					select row_number() over() id, generate_series as num from (select * from generate_series(0, $1))xxx
					where mod(generate_series,2) = 0
					)xxx where id = $2' INTO num using parcel_count, find_id;
	else
		EXECUTE 'select num from (
				select row_number() over() id, generate_series as num from (select * from generate_series(0, $1))xxx
				where mod(generate_series,2) <> 0
				)xxx where id = $2' into num USING parcel_count, find_id;
	end if;
else
	if start_number_type::int = 0 then
	    EXECUTE 'select num from (
					select row_number() over() id, generate_series as num from (select * from generate_series(0, $1))xxx
					where mod(generate_series,2) = 0
					)xxx where id = $2' INTO num using parcel_count, find_id;
	else
		EXECUTE 'select num from (
				select row_number() over() id, generate_series as num from (select * from generate_series(0, $1))xxx
				where mod(generate_series,2) <> 0
				)xxx where id = $2' into num USING parcel_count, find_id;
	end if;
end if;
RETURN num;

END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

select * from base.auto_numbering_odd_even(1, 24, 4, 12);
