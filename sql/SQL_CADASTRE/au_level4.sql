-- DROP TABLE admin_units.au_level4;

CREATE TABLE admin_units.au_level4
(
  code character varying(5) PRIMARY KEY,
  name character varying(50) NOT NULL,
  area_m2 numeric,
  geometry geometry(MultiPolygon,4326),
  au1_code character varying(3) references admin_units.au_level1 on update cascade on delete restrict,
  au2_code character varying(5)references admin_units.au_level2 on update cascade on delete restrict
)
WITH (
  OIDS=FALSE
);
ALTER TABLE admin_units.au_level4
  OWNER TO geodb_admin;
GRANT ALL ON TABLE admin_units.au_level4 TO geodb_admin;
GRANT SELECT ON TABLE admin_units.au_level4 TO cadastre_view;
GRANT SELECT ON TABLE admin_units.au_level4 TO cadastre_update;
GRANT SELECT ON TABLE admin_units.au_level4 TO contracting_view;
GRANT SELECT ON TABLE admin_units.au_level4 TO contracting_update;
GRANT SELECT ON TABLE admin_units.au_level4 TO reporting;
GRANT SELECT ON TABLE admin_units.au_level4 TO role_management;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE admin_units.au_level4 TO land_office_administration;

-- Index: admin_units.st_idx_au_level4

-- DROP INDEX admin_units.st_idx_au_level4;

CREATE INDEX st_idx_au_level4
  ON admin_units.au_level4
  USING gist
  (geometry);


-- Trigger: update_area on admin_units.au_level4

DROP FUNCTION base.create_au4_code();

CREATE OR REPLACE FUNCTION base.create_au4_code()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l1_code text;
  v_admin_unit_l2_code text;
  v_parcel_prefix text;
  v_counter int;
  v_error_counter int;
  max_code int;
  max_code_txt text;

BEGIN

	NEW.geometry := st_force2d(NEW.geometry);


 IF (NEW.geometry IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	IF NOT FOUND THEN
            RAISE NOTICE 'Tosgonii hil aimagt hamaarahgui bna!';
        END IF;
	
	execute 'select max(code)::int from (
	select code from admin_units.au_level2
	where au1_code = $1
	union all
	select code from admin_units.au_level4
	where au1_code = $1)xxx' into max_code using v_admin_unit_l1_code;

	
	
	max_code := max_code + 3;
	max_code_txt := lpad(max_code::text, 5, '0');
	
	NEW.code := max_code_txt;
	NEW.au1_code := v_admin_unit_l1_code;
	NEW.au2_code := v_admin_unit_l2_code;
	
END IF;
	RAISE NOTICE  '!!!!';
    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_au4_code()
  OWNER TO geodb_admin;

----------------

DROP TRIGGER a_create_au4_code ON admin_units.au_level4;

CREATE TRIGGER a_create_au4_code
  BEFORE INSERT
  ON admin_units.au_level4
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_au4_code();
