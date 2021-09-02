CREATE OR REPLACE FUNCTION base.st_street_parcel_auto_number(in_street_id bigint)
  RETURNS boolean AS
$BODY$
DECLARE
    pad text;
begin

    EXECUTE 'with new_numbers as (
			select * from (
			select 
			(select * from base.auto_numbering_odd_even(1, (select (count(cpa.id)*2)::int from data_address.ca_parcel_address cpa where cpa.street_id = $1), num::int, 0)) as new_no, 
			* from (
			select row_number() over() as num, * from (
			select 
			st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)),
			st_distance(cpa.geometry , ss.line_geom),
			st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)) +
			st_distance(cpa.geometry , ss.line_geom),
			cpa.is_active, cpa.id, cpa.street_id, cpa.street_side, cpa.address_parcel_no, cpa.geometry, ss.line_geom, 
			(select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)
			from data_address.ca_parcel_address cpa 
			join data_address.st_street ss on cpa.street_id = ss.id 
			where cpa.is_active is true and cpa.street_side = 1 and cpa.street_id = $1
			order by st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)) + st_distance(cpa.geometry , ss.line_geom)
			)ddd
			)xxx
			)ggg order by new_no
			)
			update data_address.ca_parcel_address
			set address_parcel_no = s.new_no, updated_by = 9910, is_new_address = true, in_source = 9
			from new_numbers s
			where data_address.ca_parcel_address.id = s.id;' USING in_street_id;
			
	EXECUTE 'with new_numbers as (
			select * from (
			select 
			(select * from base.auto_numbering_odd_even(-1, (select (count(cpa.id)*2)::int from data_address.ca_parcel_address cpa where cpa.street_id = $1), num::int, 0)) as new_no, 
			* from (
			select row_number() over() as num, * from (
			select 
			st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)),
			st_distance(cpa.geometry , ss.line_geom),
			st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)) +
			st_distance(cpa.geometry , ss.line_geom),
			cpa.is_active, cpa.id, cpa.street_id, cpa.street_side, cpa.address_parcel_no, cpa.geometry, ss.line_geom, 
			(select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)
			from data_address.ca_parcel_address cpa 
			join data_address.st_street ss on cpa.street_id = ss.id 
			where cpa.is_active is true and cpa.street_side = -1 and cpa.street_id = $1
			order by st_distance(cpa.geometry , (select ssp.geometry from data_address.st_street_point ssp where ssp.point_type = 1 and ssp.street_id = cpa.street_id)) + st_distance(cpa.geometry , ss.line_geom)
			)ddd
			)xxx
			)ggg order by new_no
			)
			update data_address.ca_parcel_address
			set address_parcel_no = s.new_no, updated_by = 9910, is_new_address = true, in_source = 9
			from new_numbers s
			where data_address.ca_parcel_address.id = s.id;' USING in_street_id;

 Return 1;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.st_street_parcel_auto_number(bigint)
  OWNER TO geodb_admin;