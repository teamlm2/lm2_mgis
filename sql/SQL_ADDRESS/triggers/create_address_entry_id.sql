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
	
	EXECUTE 'SELECT ST_ClosestPoint(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))::geometry(Point,4326) FROM
	   (SELECT
	      ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
	      ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
	    FROM
	      (select st_makevalid((ST_Dump(ST_Boundary(geometry))).geom) as geom from (
		select geometry from data_address.ca_parcel_address 
		union all
		select geometry from data_address.ca_building_address 
		) parcel, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as b
		where ST_DWithin(parcel.geometry, ST_GeomFromText(b.new_geometry, 4326)::geometry(Point,4326), 0.0006)
	       ) AS linestrings
	    ) AS segments, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as pp			
		group by pp.new_geometry, sp,ep
		order by min(st_distance(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))) asc limit 1; ' INTO point_geometry; 	

	if parcel_id is null then	
		SELECT id FROM data_address.ca_parcel_address INTO parcel_id WHERE ST_COVERS(geometry, point_geometry);
	end if;
	if building_id is null then
		SELECT id FROM data_address.ca_building_address INTO building_id WHERE ST_COVERS(geometry, point_geometry);
	end if;
	
	IF (TG_OP = 'INSERT') THEN
		NEW.entrance_id := entrance_id;	
		NEW.parcel_id := parcel_id;	
		NEW.building_id := building_id;		
		NEW.geometry := point_geometry;
	ELSIF (TG_OP = 'UPDATE') THEN
		NEW.parcel_id := parcel_id;	
		NEW.building_id := building_id;		
		NEW.geometry := point_geometry;
	END IF;
	
END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_address_entry_id()
  OWNER TO geodb_admin;

DROP TRIGGER a_create_address_entry_id ON data_address.st_entrance;
CREATE TRIGGER a_create_address_entry_id
  BEFORE INSERT OR UPDATE
  ON data_address.st_entrance
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_address_entry_id();