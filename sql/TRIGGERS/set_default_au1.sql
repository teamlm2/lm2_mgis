CREATE OR REPLACE FUNCTION base.set_default_au1()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l1_code text;

BEGIN
	
 IF (NEW.geometry IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_Within(ST_PointOnSurface((NEW.geometry)), geometry);
		
	NEW.au1 := v_admin_unit_l1_code;
 END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_default_au1()
  OWNER TO geodb_admin;