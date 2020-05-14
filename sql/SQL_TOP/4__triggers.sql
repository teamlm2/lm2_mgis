-- Function: base.create_parcel_id()

-- DROP FUNCTION base.create_parcel_id();

CREATE OR REPLACE FUNCTION base.create_parcel_id()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l1_code text;
  v_admin_unit_l2_code text;
  v_cblock_code text;
  v_parcel_prefix text;
  v_counter int;
  v_ub_counter int;
  v_error_counter int;
  v_pa_from date;
  v_pa_till date;
  org_type int;
  pid text;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);
	
	IF (NEW.parcel_id IS NULL) THEN
		pid := NEW.parcel_id;
	END IF;
	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

  SELECT pa_from INTO v_pa_from FROM settings.set_role_user where user_name = current_user;
  SELECT pa_till INTO v_pa_till FROM settings.set_role_user where user_name = current_user;
  SELECT organization INTO org_type FROM settings.set_role_user where user_name = current_user;

  UPDATE settings.set_role_user SET pa_from = '1800-01-01' where user_name = current_user;
  UPDATE settings.set_role_user SET pa_till = 'infinity' where user_name = current_user;

 	IF (NEW.geometry IS NOT NULL) THEN
		
        SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_COVERS(geometry, NEW.geometry);
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, NEW.geometry);
        IF NOT FOUND THEN
            RAISE NOTICE 'No Aimag / Duureg found around the parcel, parcel will have an error code!';
        END IF;

        SELECT code FROM admin_units.au_cadastre_block INTO v_cblock_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
        IF NOT FOUND THEN
            RAISE NOTICE 'No cadastre block found around the parcel, parcel will have an error code!';
        END IF;

        v_parcel_prefix := v_cblock_code;

        execute 'SELECT max(substring(parcel_id from 6 for 5)::int) FROM data_top.ca_union_parcel WHERE parcel_id LIKE $1' into v_counter using v_parcel_prefix || '%';
		execute 'SELECT max(substring(parcel_id from 6 for 5)::int) FROM data_ub.ca_ub_parcel WHERE au2 = '''||v_admin_unit_l2_code||''' and parcel_id LIKE $1' into v_ub_counter using v_parcel_prefix || '%';
        if v_counter < v_ub_counter then
			v_counter := v_ub_counter;
		end if;
			IF v_counter IS NULL THEN
				v_counter := v_ub_counter;
			END IF;
			
			if v_counter is null then
				v_counter := 0;
			end if;
			v_counter := v_counter + 1;
			
			IF (NEW.parcel_id IS NULL) THEN
				RAISE NOTICE 'new';
				IF (v_cblock_code || lpad(v_counter::text, 5, '0')) IS NULL THEN
					execute 'SELECT max(substring(parcel_id from 11 for 7)::int) FROM data_top.ca_union_parcel WHERE au2 = '''||v_admin_unit_l2_code||''' and parcel_id LIKE $1' into v_error_counter using 'ER%';
					IF v_error_counter IS NULL THEN
						v_error_counter := 0;
					END IF;
					v_error_counter := v_error_counter + 1;
					NEW.parcel_id := 'E' ||v_admin_unit_l2_code::int::text|| lpad(v_error_counter::text, 5, '0');
				ELSE
					NEW.parcel_id := v_cblock_code || lpad(v_counter::text, 5, '0');
				END IF;
			ELSE
				IF CHAR_LENGTH(NEW.parcel_id) != 10 THEN
					RAISE NOTICE 'new';
					IF (v_cblock_code || lpad(v_counter::text, 5, '0')) IS NULL THEN
						execute 'SELECT max(substring(parcel_id from 11 for 7)::int) FROM data_top.ca_union_parcel WHERE au2 = '''||v_admin_unit_l2_code||''' and parcel_id LIKE $1' into v_error_counter using 'ER%';
						IF v_error_counter IS NULL THEN
							v_error_counter := 0;
						END IF;
						v_error_counter := v_error_counter + 1;
						NEW.parcel_id := 'E' ||v_admin_unit_l2_code::int::text|| lpad(v_error_counter::text, 5, '0');
					ELSE
						NEW.parcel_id := v_cblock_code || lpad(v_counter::text, 5, '0');
					END IF;
				ELSE
					NEW.parcel_id := NEW.parcel_id;
				END IF;
			END IF;
			IF (org_type IS NULL) THEN
				org_type :=  1;
			END IF;
			
			NEW.au2 := v_admin_unit_l2_code;
			NEW.org_type := org_type;
		END IF;

    UPDATE settings.set_role_user SET pa_from = v_pa_from where user_name = current_user;
    UPDATE settings.set_role_user SET pa_till = v_pa_till where user_name = current_user;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_parcel_id()
  OWNER TO geodb_admin;
