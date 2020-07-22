-- Function: base.parcel_clip_to_gns()

-- DROP FUNCTION base.parcel_clip_to_gns();

CREATE OR REPLACE FUNCTION base.parcel_clip_to_gns()
  RETURNS trigger AS
$BODY$
DECLARE
  parcel_id int;
  new_geometry geometry(Polygon,4326);
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

	IF (NEW.geometry IS NOT NULL) THEN

		EXECUTE 'with new_numbers as (
				WITH gns AS (
					select l.parcel_id, l.geometry from data_landuse.ca_landuse_type_tbl l
					where l.is_active = true and st_overlaps(l.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))
					)
				SELECT parcel_id, 
				(ST_DUMP(ST_Difference(
							f.geometry,        
							(
								select (ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)::geometry(Polygon, 4326))
							)
						))).geom::geometry(Polygon,4326) as geometry
				FROM gns f
			)
			update data_landuse.ca_landuse_type_tbl
			  set geometry = s.geometry
			from new_numbers s
			where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id;';
		EXECUTE 'insert into data_landuse.ca_landuse_type_tbl (landuse, geometry) values('''||NEW.landuse||''', ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))';
	END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.parcel_clip_to_gns()
  OWNER TO geodb_admin;

DROP TRIGGER a_parcel_clip_to_gns ON data_soums_union.ca_parcel_tbl;
CREATE TRIGGER a_parcel_clip_to_gns
  BEFORE INSERT OR UPDATE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.parcel_clip_to_gns();
