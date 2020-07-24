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
					select l.parcel_id, st_makevalid(l.geometry) as geometry from data_landuse.ca_landuse_type_tbl l
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
			  set is_active = false, valid_till = now(), is_overlaps_historiy = true
			from new_numbers s
			where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id;';		

		EXECUTE 'insert into data_landuse.ca_landuse_type_tbl(is_active, landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood, geometry)			
				WITH gns AS (
					select l.parcel_id, st_makevalid(l.geometry) as geometry, l.landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood from data_landuse.ca_landuse_type_tbl l
					where l.is_overlaps_historiy = true and st_overlaps(l.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))
					)
				SELECT true, landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood, 
				(ST_DUMP(ST_Difference(
							f.geometry,        
							(
								select (ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326)::geometry(Polygon, 4326))
							)
						))).geom::geometry(Polygon,4326) as geometry
				FROM gns f;';

		EXECUTE 'insert into data_landuse.ca_landuse_type_tbl (is_active, landuse, geometry) values(true, '''||NEW.landuse||''', ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326));';

		EXECUTE 'with new_numbers as (
				WITH gns AS (
					select l.parcel_id, st_makevalid(l.geometry) as geometry from data_landuse.ca_landuse_type_tbl l
					where l.is_overlaps_historiy = true and st_overlaps(l.geometry, ST_GeomFromText('''||ST_AsText(NEW.geometry)||'''::text, 4326))
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
			  set is_overlaps_historiy = false
			from new_numbers s
			where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id;';	
				
	END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.parcel_clip_to_gns()
  OWNER TO geodb_admin;

DROP TRIGGER if exists a_parcel_clip_to_gns ON data_soums_union.ca_parcel_tbl;
CREATE TRIGGER a_parcel_clip_to_gns
  BEFORE INSERT OR UPDATE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.parcel_clip_to_gns();
