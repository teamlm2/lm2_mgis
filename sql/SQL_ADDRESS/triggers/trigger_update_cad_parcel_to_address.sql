-- Function: base.update_cad_parcel_to_address()

-- DROP FUNCTION base.update_cad_parcel_to_address();

CREATE OR REPLACE FUNCTION base.update_cad_parcel_to_address()
  RETURNS trigger AS
$BODY$
DECLARE
  parcel_id text;
  new_geometry geometry(Polygon,4326);
  address_khashaa text;
  address_streetname text;
  address_neighbourhood text;
  valid_till date;
BEGIN
	address_khashaa := '';
	address_streetname := '';
	address_neighbourhood := '';
	parcel_id := '';
	valid_till := null;	

	IF (TG_OP = 'INSERT') THEN
		
		NEW.geometry := st_force2d(NEW.geometry);
		IF (NEW.parcel_id IS NOT NULL) THEN	
			parcel_id := NEW.parcel_id;
		END IF;

		IF (NEW.address_khashaa IS NOT NULL) THEN	
			address_khashaa := NEW.address_khashaa;
		END IF;

		IF (NEW.address_streetname IS NOT NULL) THEN	
			address_streetname := NEW.address_streetname;
		END IF;

		IF (NEW.address_neighbourhood IS NOT NULL) THEN	
			address_neighbourhood := NEW.address_neighbourhood;
		END IF;
		
		IF (NEW.valid_from IS NULL) THEN
			NEW.valid_from := now();
		END IF;
		IF (NEW.valid_till IS NOT NULL) THEN	
			valid_till := NEW.valid_till;
		END IF;
		
		RAISE NOTICE 'parcel_id (%)',  parcel_id;

		IF (NEW.geometry IS NOT NULL) THEN			
			EXECUTE 'with new_numbers as (
					select l.id, st_makevalid(l.geometry) as geometry from data_address.ca_parcel_address l
						where l.is_active = true and (st_overlaps(l.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)) or st_covers(l.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)))
				)
				update data_address.ca_parcel_address
				  set is_active = false, valid_till = now()
				from new_numbers s
				where data_address.ca_parcel_address.id = s.id and not st_equals(data_address.ca_parcel_address.geometry, s.geometry);';		
	---
			EXECUTE 'insert into data_address.ca_parcel_address (parcel_id, is_active, landuse, address_parcel_no, address_streetname, address_neighbourhood, created_at, updated_at, parcel_type, status, in_source, is_marked, geometry) 
			values('''||parcel_id||''', true, '''||NEW.landuse||''', '''||address_khashaa||''', '''||address_streetname||''', '''||address_neighbourhood||''', now(), now(), 1, 1, 1, false, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))';
				
		END IF;
	END IF;
	IF (TG_OP = 'UPDATE') THEN
		IF (NEW.valid_till IS NOT NULL) THEN	
			valid_till := NEW.valid_till;
		END IF;

		EXECUTE 'with new_numbers as (select cpa.id, cpa.parcel_id, landuse, cpa.valid_from, cpa.valid_till, case when '''||NEW.valid_till||'''::date <= now() then false else true end is_active,
			(select geometry from data_soums_union.ca_parcel_tbl cpa where cpa.parcel_id = '''||OLD.parcel_id||''') as new_geom
			from data_address.ca_parcel_address cpa 
			where (st_overlaps(cpa.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))  or st_covers(cpa.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)))
				)
				update data_address.ca_parcel_address
				  set is_active = false, landuse = '''||NEW.landuse||''', valid_till = '''||valid_till||'''::date, geometry = s.new_geom
				from new_numbers s
				where data_address.ca_parcel_address.id = s.id';

		EXECUTE 'with new_numbers as (select cpa.id, cpa.parcel_id, landuse, cpa.valid_from, cpa.valid_till, case when '''||NEW.valid_till||'''::date <= now() then false else true end is_active,
			(select geometry from data_soums_union.ca_parcel_tbl cpa where cpa.parcel_id = '''||OLD.parcel_id||''') as new_geom
			from data_address.ca_parcel_address cpa 
			where cpa.parcel_id = '''||OLD.parcel_id||''' and (st_overlaps(cpa.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))  or st_covers(cpa.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)))
				)
				update data_address.ca_parcel_address
				  set is_active = s.is_active, landuse = '''||NEW.landuse||''', valid_till = '''||valid_till||'''::date, geometry = s.new_geom
				from new_numbers s
				where data_address.ca_parcel_address.id = s.id';				

	END IF;
	IF (TG_OP = 'DELETE') THEN
		IF (OLD.parcel_id IS NOT NULL) THEN			
			EXECUTE 'with new_numbers as (select cpa.id, cpa.parcel_id, cpa.geometry, cpa.valid_from, cpa.valid_till from data_address.ca_parcel_address cpa 
						where cpa.is_active = true and cpa.parcel_id = '''||OLD.parcel_id||''' and (st_overlaps(cpa.geometry, ST_GeomFromText('''||ST_AsText(OLD.geometry)||'''::text, 4326))  or st_covers(cpa.geometry, ST_GeomFromText('''||ST_AsText(OLD.geometry)||'''::text, 4326)))
							)
							update data_address.ca_parcel_address
							  set is_active = false, valid_till = '''||OLD.valid_till||'''::date
							from new_numbers s
							where data_address.ca_parcel_address.id = s.id';
		END IF;
	END IF;
	RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.update_cad_parcel_to_address()
  OWNER TO geodb_admin;


DROP TRIGGER if exists a_update_cad_parcel_to_address ON data_soums_union.ca_parcel_tbl;
CREATE TRIGGER a_update_cad_parcel_to_address
  AFTER INSERT OR UPDATE OR DELETE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_cad_parcel_to_address();
