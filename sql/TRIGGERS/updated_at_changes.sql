CREATE OR REPLACE FUNCTION base.updated_at_changes()
  RETURNS trigger AS
$BODY$
BEGIN        
	IF (TG_OP = 'UPDATE') THEN
		NEW.updated_at := now();
	ELSIF (TG_OP = 'INSERT') THEN
		NEW.created_at := now();
		NEW.updated_at := now();
	END IF;
	RETURN new;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.updated_at_changes()
  OWNER TO geodb_admin;

DROP TRIGGER a_updated_at_changes ON data_soums_union.ca_parcel_tbl;
CREATE TRIGGER a_updated_at_changes
  BEFORE INSERT OR UPDATE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.updated_at_changes();

update data_soums_union.ca_parcel_tbl set address_khashaa = '11' where parcel_id = '1801811347';

update data_soums_union.ca_parcel_tbl set updated_at = now() where parcel_id = '1801811347';

update data_soums_union.ca_parcel_tbl set updated_at = null where parcel_id = '1801811347';

select updated_at from data_soums_union.ca_parcel_tbl where parcel_id = '1801811347';
