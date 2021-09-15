-- Function: base.update_geometry_entry()

-- DROP FUNCTION base.update_geometry_entry();

CREATE OR REPLACE FUNCTION base.update_geometry_entry()
  RETURNS trigger AS
$BODY$
DECLARE
  a_parcel_id int;
  a_building_id int;
  v_counter int;
  temp_id int;
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
	
	entry_no := 1;
        a_parcel_id:= NULL;
        a_building_id:= NULL;
	if NEW.name IS NULL THEN
		SELECT description FROM data_address.cl_entry_type INTO entry_name WHERE code = NEW.type;
	END IF;
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, new_geometry);


	EXECUTE 'SELECT l_type, id, ST_ClosestPoint(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))::geometry(Point,4326) as p_geom FROM
	   (SELECT l_type, id,
		  ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
		  ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
		FROM
		  (select l_type, id, st_makevalid((ST_Dump(ST_Boundary(geometry))).geom) as geom from (
		select 1 as l_type, id, geometry from data_address.ca_parcel_address where now() between valid_from and valid_till
		union all
		select 2 as l_type, id, geometry from data_address.ca_building_address where now() between valid_from and valid_till
		) parcel, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as b
		where ST_DWithin(parcel.geometry, ST_GeomFromText(b.new_geometry, 4326)::geometry(Point,4326), 0.0006)
		   ) AS linestrings
		) AS segments, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as pp
		group by pp.new_geometry, sp,ep, l_type, id
		order by min(st_distance(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))) asc limit 1; ' INTO v_type, temp_id, point_geometry;

	if v_type = 1 then
		a_parcel_id := temp_id;
	elsif v_type = 2 then
		a_building_id := temp_id;
	end if;

	--entry no generate

	
	if entry_no_counter is null then
		entry_no_counter := 0;
	end if;
	entry_no_counter := entry_no_counter + 1;
	entry_no := entry_no_counter;
	
	IF NEW.name is null THEN
		NEW.name := entry_name;
	END IF;

	IF (TG_OP = 'INSERT') THEN
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
ALTER FUNCTION base.update_geometry_entry()
  OWNER TO geodb_admin;
