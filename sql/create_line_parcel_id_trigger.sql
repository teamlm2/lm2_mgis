-- Function: base.create_parcel_id()

-- DROP FUNCTION base.create_parcel_id();

CREATE OR REPLACE FUNCTION base.create_line_parcel_id()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l1_code text;
  v_admin_unit_l2_code text;
  v_parcel_prefix text;
  v_counter int;
  v_error_counter int;
  v_pa_from date;
  v_pa_till date;
  parcel_no text;
BEGIN

	NEW.line_geom := st_force2d(NEW.line_geom);
	
	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

  SELECT pa_from INTO v_pa_from FROM settings.set_role where user_name = current_user;
  SELECT pa_till INTO v_pa_till FROM settings.set_role where user_name = current_user;

  UPDATE settings.set_role SET pa_from = '1800-01-01' where user_name = current_user;
  UPDATE settings.set_role SET pa_till = 'infinity' where user_name = current_user;

 IF (NEW.line_geom IS NOT NULL) THEN
		
        SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_COVERS(geometry, NEW.line_geom);
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, NEW.line_geom);
	SELECT parcel_id FROM data_soums_union.ca_parcel_tbl INTO parcel_no WHERE ST_COVERS(geometry, NEW.line_geom);
	
	IF (parcel_no IS NULL) THEN
		execute 'SELECT max(substring(parcel_id, 3, 8)::int) FROM data_soums_union.ca_parcel_line_tbl WHERE parcel_id LIKE $1' into v_error_counter using 'ER%';
		IF v_error_counter IS NULL THEN
			v_error_counter := 0;
		END IF;
		v_error_counter := v_error_counter + 1;
		NEW.sub_parcel_id := 'ER' || lpad(v_error_counter::text, 8, '0');
	ELSE		
		NEW.parcel_id := parcel_no;
	END IF;
	NEW.au2 := v_admin_unit_l2_code;
	
END IF;

    UPDATE settings.set_role SET pa_from = v_pa_from where user_name = current_user;
    UPDATE settings.set_role SET pa_till = v_pa_till where user_name = current_user;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_line_parcel_id()
  OWNER TO geodb_admin;


CREATE TRIGGER a_create_line_parcel_id
  BEFORE INSERT
  ON data_soums_union.ca_parcel_line_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_line_parcel_id();