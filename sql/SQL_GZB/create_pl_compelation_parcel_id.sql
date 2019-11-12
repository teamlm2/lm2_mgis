CREATE OR REPLACE FUNCTION base.create_pl_compelation_parcel_id()
  RETURNS trigger AS
$BODY$
DECLARE
  parcel_no int;
  project_no int;
  v_counter int;
BEGIN
  NEW.geometry := st_force2d(NEW.geometry);

  SELECT parcel_id FROM data_plan.pl_project_parcel INTO parcel_no WHERE ST_COVERS(polygon_geom, ST_CENTROID(NEW.geometry));
  SELECT project_id FROM data_plan.pl_project_parcel INTO project_no WHERE ST_COVERS(polygon_geom, ST_CENTROID(NEW.geometry));
  
 IF (NEW.geometry IS NOT NULL) THEN
	
	IF (parcel_no IS NULL) THEN
		NEW.parcel_id := NULL;	
	ELSE	
		execute 'SELECT max(id) FROM data_plan.pl_completion_parcel_tbl ' into v_counter;
		IF v_counter IS NULL THEN
			v_counter := 0;
		END IF;
		v_counter := v_counter + 1;
		NEW.id := v_counter;
		NEW.parcel_id := parcel_no;
		NEW.project_id := project_no;
	END IF;

END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_pl_compelation_parcel_id()
  OWNER TO geodb_admin;

------------
CREATE TRIGGER a_create_pl_compelation_parcel_id
  BEFORE INSERT
  ON data_plan.pl_completion_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_pl_compelation_parcel_id();