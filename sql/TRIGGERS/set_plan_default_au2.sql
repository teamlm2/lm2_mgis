DROP TRIGGER set_plan_default_au2 ON data_plan.pl_project_parcel;

CREATE OR REPLACE FUNCTION base.set_plan_default_au2()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l2_code text;

BEGIN
	
 IF (NEW.polygon_geom IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_Within(ST_PointOnSurface((NEW.polygon_geom)), geometry);
		
	NEW.au2 := v_admin_unit_l2_code;
 END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_plan_default_au2()
  OWNER TO geodb_admin;

CREATE TRIGGER set_plan_default_au2
  BEFORE INSERT
  ON data_plan.pl_project_parcel
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_plan_default_au2();

-----------------------

DROP TRIGGER set_plan_default_au1 ON data_plan.pl_project_parcel;

CREATE OR REPLACE FUNCTION base.set_plan_default_au1()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l1_code text;

BEGIN
	
 IF (NEW.polygon_geom IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_Within(ST_PointOnSurface((NEW.polygon_geom)), geometry);
		
	NEW.au1 := v_admin_unit_l1_code;
 END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_plan_default_au1()
  OWNER TO geodb_admin;

CREATE TRIGGER set_plan_default_au1
  BEFORE INSERT
  ON data_plan.pl_project_parcel
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_plan_default_au1();