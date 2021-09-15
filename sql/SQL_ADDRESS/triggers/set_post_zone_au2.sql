-- Function: base.set_post_zone_au2()

-- DROP FUNCTION base.set_post_zone_au2();

CREATE OR REPLACE FUNCTION base.set_post_zone_au2()
  RETURNS trigger AS
$BODY$
DECLARE

  v_admin_unit_l2_code text;
  v_au_post_zone_id int;

BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

 IF (NEW.geometry IS NOT NULL) THEN
  
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_Within(st_centroid(NEW.geometry), geometry);
	SELECT id FROM data_address.au_zipcode_area INTO v_au_post_zone_id WHERE ST_Within(st_centroid(NEW.geometry), geometry);

	NEW.au2 := v_admin_unit_l2_code;
	NEW.zipcode_id := v_au_post_zone_id;


END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_post_zone_au2()
  OWNER TO geodb_admin;


CREATE TRIGGER a_set_post_zone_au2
  BEFORE INSERT OR UPDATE
  ON data_address.ca_parcel_address
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_post_zone_au2();
--ALTER TABLE data_address.ca_parcel_address DISABLE TRIGGER a_create_address_parcel;

CREATE TRIGGER a_set_post_zone_au2
  BEFORE INSERT OR UPDATE
  ON data_address.ca_building_address
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_post_zone_au2();