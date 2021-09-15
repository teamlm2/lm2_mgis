-- Function: base.create_road_id()

-- DROP FUNCTION base.create_road_id();

CREATE OR REPLACE FUNCTION base.create_road_id()
  RETURNS trigger AS
$BODY$
DECLARE

  v_counter int;
  v_error_counter int;

BEGIN
	execute 'SELECT max(id) FROM data_address.st_road ' into v_counter ;
	IF v_counter IS NULL THEN
		v_counter := 0;
	END IF;
	v_counter := v_counter + 1;
	
	IF (TG_OP = 'INSERT') THEN
		NEW.id := v_counter;	
	END IF;		

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_road_id()
  OWNER TO geodb_admin;

CREATE TRIGGER a_create_road_id
  BEFORE INSERT
  ON data_address.st_road
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_road_id();