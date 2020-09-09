-- Function: base.create_address_entry_id()

-- DROP FUNCTION base.create_address_entry_id();

CREATE OR REPLACE FUNCTION base.create_address_entry_id()
  RETURNS trigger AS
$BODY$
DECLARE
  entrance_id int;
  a_parcel_id int;
  a_building_id int;
  v_counter int;
  point_geometry geometry(Point,4326);
  new_geometry geometry(Point,4326);
  v_admin_unit_l1_code text;
  v_admin_unit_l2_code text;
  v_admin_unit_l3_code text;
  v_au_khoroolol_id int; 
  v_street_id int; 
  v_au_post_zone_id int; 
  address_streetname text;
  v_address_parcel_no text;
  v_address_building_no text;
  v_type int;
  entry_no int;
  entry_no_counter int;
  entry_name text;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

 IF (NEW.geometry IS NOT NULL) THEN
	new_geometry := NEW.geometry;
	execute 'SELECT max(entrance_id::int) FROM data_address.st_entrance' into v_counter;
	if v_counter is null then
			v_counter := 0;
		end if;
		v_counter := v_counter + 1;
		entrance_id := v_counter;
		entry_no := 1;
	if NEW.name IS NULL THEN
		SELECT description FROM data_address.cl_entry_type INTO entry_name WHERE code = NEW.type;
	END IF;
	SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_COVERS(geometry, new_geometry);
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, new_geometry);
	SELECT code FROM admin_units.au_level3 INTO v_admin_unit_l3_code WHERE ST_COVERS(geometry, new_geometry);
	SELECT fid FROM admin_units.au_khoroolol INTO v_au_khoroolol_id WHERE ST_COVERS(geometry, new_geometry);
	IF (NEW.parcel_id IS NULL) THEN
	
	
	SELECT id FROM data_address.ca_parcel_address INTO a_parcel_id WHERE ST_COVERS(geometry, NEW.geometry) and now() between valid_from and valid_till;
	SELECT id FROM data_address.ca_building_address INTO a_building_id WHERE ST_COVERS(geometry, NEW.geometry) and now() between valid_from and valid_till;

	EXECUTE 'SELECT ST_ClosestPoint(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))::geometry(Point,4326) FROM
	   (SELECT
		  ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
		  ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
		FROM
		  (select st_makevalid((ST_Dump(ST_Boundary(geometry))).geom) as geom from (
		select geometry from data_address.ca_parcel_address where now() between valid_from and valid_till
		union all
		select geometry from data_address.ca_building_address where now() between valid_from and valid_till
		) parcel, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as b
		where ST_DWithin(parcel.geometry, ST_GeomFromText(b.new_geometry, 4326)::geometry(Point,4326), 0.0006)
		   ) AS linestrings
		) AS segments, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as pp
		group by pp.new_geometry, sp,ep
		order by min(st_distance(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))) asc limit 1; ' INTO point_geometry;

	if NEW.parcel_id is null then
		SELECT id FROM data_address.ca_parcel_address INTO a_parcel_id WHERE ST_COVERS(geometry, point_geometry);
	end if;
	if NEW.building_id is null then
		SELECT id FROM data_address.ca_building_address INTO a_building_id WHERE ST_COVERS(geometry, point_geometry);
	end if;

	--entry no generate
	EXECUTE 'select type from
			(
			SELECT
				  ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
				  ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep, type, id
				FROM
				  (select st_makevalid((ST_Dump(ST_Boundary(parcel.geometry))).geom) as geom, type, id from (
				select p.geometry, 1 as type, p.parcel_id as id from data_address.ca_parcel_address p where now() between valid_from and valid_till and ST_COVERS(p.geometry, ST_GeomFromText('''||ST_AsText(point_geometry)||'''::text, 4326))
				union all
				select p.geometry, 2 as type, p.building_id as id from data_address.ca_building_address p where now() between valid_from and valid_till and ST_COVERS(p.geometry, ST_GeomFromText('''||ST_AsText(point_geometry)||'''::text, 4326))
				) parcel, (select ST_GeomFromText('''||ST_AsText(point_geometry)||'''::text, 4326) as new_geometry) as b
				--where ST_DWithin(parcel.geometry, b.new_geometry, 0.0006)
				   ) AS linestrings
			) as xxx
			group by type limit 1;' INTO v_type;

	if v_type = 1 then
		EXECUTE 'select max(address_entry_no::int) from data_address.st_entrance e, data_address.ca_parcel_address p
				where type = '''|| NEW.type ||''' and now() between p.valid_from and p.valid_till and ST_COVERS(p.geometry, ST_GeomFromText('''||ST_AsText(point_geometry)||'''::text, 4326));' INTO entry_no_counter;
	elsif v_type = 2 then
		EXECUTE 'select max(address_entry_no::int) from data_address.st_entrance e, data_address.ca_building_address p
				where type = '''|| NEW.type ||''' and now() between p.valid_from and p.valid_till and ST_COVERS(p.geometry, ST_GeomFromText('''||ST_AsText(point_geometry)||'''::text, 4326));' INTO entry_no_counter;
	end if;
	if entry_no_counter is null then
		entry_no_counter := 0;
	end if;
	entry_no_counter := entry_no_counter + 1;
	entry_no := entry_no_counter;
	--entry_no := entry_no;
	--spatial refference
	
	if a_parcel_id is null then
		SELECT id FROM data_address.ca_parcel_address INTO a_parcel_id WHERE ST_Intersects(geometry, point_geometry) and now() between valid_from and valid_till;
	end if;
	if a_building_id is null then
		SELECT id FROM data_address.ca_building_address INTO a_building_id WHERE ST_Intersects(geometry, point_geometry) and now() between valid_from and valid_till;
	end if;
	--SELECT id FROM data_address.st_street INTO v_street_id WHERE ST_COVERS(geometry, point_geometry);
	SELECT name || '-' || code FROM data_address.st_street_sub INTO address_streetname WHERE ST_COVERS(geometry, point_geometry);
	SELECT id FROM data_address.au_zipcode_area INTO v_au_post_zone_id WHERE ST_COVERS(geometry, point_geometry);
	SELECT address_building_no FROM data_address.ca_building_address INTO v_address_building_no WHERE ST_COVERS(geometry, point_geometry) and now() between valid_from and valid_till;
	SELECT address_parcel_no FROM data_address.ca_parcel_address INTO v_address_parcel_no WHERE ST_COVERS(geometry, point_geometry) and now() between valid_from and valid_till;
	
	IF NEW.name is null THEN
		NEW.name := entry_name;
	END IF;

	IF (TG_OP = 'INSERT') THEN
		--NEW.entrance_id := entrance_id;
		NEW.address_entry_no := entry_no;
		NEW.created_at := now();
		NEW.is_active := true;		
	END IF;	
	NEW.parcel_id := a_parcel_id;
	NEW.building_id := a_building_id;
	NEW.geometry := point_geometry;
	
	--NEW.street_id := v_street_id;
	NEW.address_streetname := address_streetname;
	NEW.zipcode_id := v_au_post_zone_id;
	NEW.address_parcel_no := v_address_parcel_no;
	NEW.address_building_no := v_address_building_no;
	NEW.updated_at := now();

	END IF;
	IF (TG_OP = 'INSERT') THEN
		NEW.entrance_id := entrance_id;
		NEW.address_entry_no := entry_no;
		NEW.created_at := now();
		NEW.is_active := true;	
	END IF;
	NEW.updated_at := now();
	NEW.au1 := v_admin_unit_l1_code;
	NEW.au2 := v_admin_unit_l2_code;
	NEW.au3 := v_admin_unit_l3_code;
	NEW.khoroolol_id := v_au_khoroolol_id;
END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_address_entry_id()
  OWNER TO geodb_admin;
