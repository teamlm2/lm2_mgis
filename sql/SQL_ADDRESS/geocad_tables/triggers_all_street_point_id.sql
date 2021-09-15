set search_path to data_address;



-- DROP FUNCTION base.all_street_point_id();

CREATE OR REPLACE FUNCTION base.all_street_point_id()
  RETURNS trigger AS
$BODY$
DECLARE
  entrance_id int;
  v_counter int;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

 IF (NEW.geometry IS NOT NULL) THEN

	execute 'SELECT max(id::int) FROM data_address.all_street_point' into v_counter;

	if v_counter is null then
		v_counter := 0;
	end if;
	v_counter := v_counter + 1;
	entrance_id := v_counter;

	IF (TG_OP = 'INSERT') THEN
		NEW.id := entrance_id;
	END IF;	
	

END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.all_street_point_id()
  OWNER TO geodb_admin;
	
	
CREATE TRIGGER a_all_street_point_id
  BEFORE INSERT OR UPDATE
  ON data_address.all_street_point
  FOR EACH ROW
  EXECUTE PROCEDURE base.all_street_point_id();