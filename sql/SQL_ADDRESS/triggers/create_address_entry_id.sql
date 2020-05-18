-- Function: base.create_parcel_id()

-- DROP FUNCTION base.create_parcel_id();

CREATE OR REPLACE FUNCTION base.create_address_entry_id()
  RETURNS trigger AS
$BODY$
DECLARE
  entrance_id int;
  parcel_id int;
  building_id int;
  v_counter int;
  point_geometry geometry(Point,4326);
  new_geometry geometry(Point,4326);
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);
	
	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;
	
 IF (NEW.geometry IS NOT NULL) THEN
	new_geometry := NEW.geometry;
	execute 'SELECT max(entrance_id) FROM data_address.st_entrance' into v_counter;

	if v_counter is null then
		v_counter := 0;
	end if;
	v_counter := v_counter + 1;
	entrance_id := v_counter;

	SELECT id FROM data_address.ca_parcel_address INTO parcel_id WHERE ST_COVERS(geometry, NEW.geometry);
	SELECT id FROM data_address.ca_building_address INTO building_id WHERE ST_COVERS(geometry, NEW.geometry);

	IF parcel_id is not null then
		EXECUTE 'SELECT ST_ClosestPoint(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))::geometry(Point,4326) FROM
		   (SELECT
		      ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
		      ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
		    FROM
		      (SELECT (ST_Dump(ST_Boundary(geometry))).geom
		       FROM data_address.ca_parcel_address where id = ''' || parcel_id || '''
		       ) AS linestrings
		    ) AS segments, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as pp
			group by pp.new_geometry, sp,ep
			order by min(st_distance(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))) asc limit 1;' INTO point_geometry; 
	end if; 
	--UPDATE data_address.st_entrance SET geometry = point_geometry where data_address.st_entrance.entrance_id = entrance_id;
NEW.entrance_id := entrance_id;	
	NEW.parcel_id := parcel_id;	
	NEW.building_id := building_id;		
NEW.geometry := point_geometry;
END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_address_entry_id()
  OWNER TO geodb_admin;


CREATE TRIGGER a_create_address_entry_id
  BEFORE INSERT
  ON data_address.st_entrance
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_address_entry_id();