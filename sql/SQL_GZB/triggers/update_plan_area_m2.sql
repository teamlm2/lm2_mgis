CREATE OR REPLACE FUNCTION base.update_plan_area_m2()
  RETURNS trigger AS
$BODY$
DECLARE
	v_geometry_type text;
	parcel_area_m2 numeric;
BEGIN
	IF NEW.source_parcel_id IS NULL THEN
		IF (NOT (NEW.polygon_geom IS NULL)) and st_y(st_centroid(NEW.polygon_geom)) < 200 THEN
			v_geometry_type := ST_GeometryType(NEW.polygon_geom);
			IF (v_geometry_type ILIKE '%POLYGON%') THEN
				NEW.area_m2 := base.calculate_area_utm(NEW.polygon_geom);
			END IF;
		END IF;
	ELSE
		SELECT area_m2 FROM data_plan.pl_project_parcel INTO parcel_area_m2 WHERE parcel_id = NEW.source_parcel_id;
		NEW.area_m2 := parcel_area_m2;
	END IF;
	

	RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.update_plan_area_m2()
  OWNER TO geodb_admin;

DROP TRIGGER update_area_m2 ON data_plan.pl_project_parcel;
CREATE TRIGGER update_area_m2
  BEFORE INSERT OR UPDATE
  ON data_plan.pl_project_parcel
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_plan_area_m2();

-----------------------

with new_numbers as (
select b.parcel_id as aa, p.parcel_id, p.plan_zone_id, p.area_m2 cur_area, b.area_m2, p.source_parcel_id from data_plan.pl_project_parcel p, data_plan.pl_project_parcel b
where p.source_parcel_id is not null and p.source_parcel_id = b.parcel_id
)
update data_plan.pl_project_parcel
set area_m2 = s.area_m2
from new_numbers s
where data_plan.pl_project_parcel.parcel_id = s.parcel_id and data_plan.pl_project_parcel.source_parcel_id is not null;
