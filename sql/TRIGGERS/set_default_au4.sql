CREATE OR REPLACE FUNCTION base.set_default_au4()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l4_code text;

BEGIN
	
 IF (NEW.geometry IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level4 INTO v_admin_unit_l4_code WHERE ST_Within(ST_Centroid(NEW.geometry), geometry);
		
	NEW.au4 := v_admin_unit_l4_code;
 END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_default_au4()
  OWNER TO geodb_admin;

CREATE TRIGGER set_default_au4
  BEFORE INSERT OR UPDATE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au4();