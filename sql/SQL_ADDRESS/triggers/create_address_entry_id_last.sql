-- Function: base.create_address_entry_id()

-- DROP FUNCTION base.create_address_entry_id();

CREATE OR REPLACE FUNCTION base.create_address_entry_id()
  RETURNS trigger AS
$BODY$
DECLARE
  entrance_id int;
  v_counter int;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

 IF (NEW.geometry IS NOT NULL) THEN

	execute 'SELECT max(entrance_id::int) FROM data_address.st_entrance' into v_counter;
	if v_counter is null then
		v_counter := 0;
	end if;
	v_counter := v_counter + 1;
	entrance_id := v_counter;

	IF (TG_OP = 'INSERT') THEN
		NEW.entrance_id := entrance_id;
		NEW.address_entry_no := '1';
		NEW.created_at := now();
		NEW.updated_at := now();
	END IF;
	
END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_address_entry_id()
  OWNER TO geodb_admin;
