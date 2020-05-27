-- Function: base.create_address_parcel()

-- DROP FUNCTION base.create_address_parcel();

CREATE OR REPLACE FUNCTION base.create_address_parcel()
  RETURNS trigger AS
$BODY$
DECLARE
  v_id int;
  parcel_id int;
  building_id int;
  v_counter int;
  point_geometry geometry(Point,4326);
  new_geometry geometry(Point,4326);
  v_admin_unit_l1_code text;
  v_admin_unit_l2_code text;
  v_admin_unit_l3_code text;
  v_au_khoroolol_id int;
  v_street_sub_id int;
  v_au_post_zone_id int;
  address_streetname text;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

	IF (NEW.valid_from IS NULL) THEN
		NEW.valid_from := now();
	END IF;

 IF (NEW.geometry IS NOT NULL) THEN
-- 	new_geometry := NEW.geometry;
	execute 'SELECT max(id::int) FROM data_address.ca_parcel_address' into v_counter;

	if v_counter is null then
		v_counter := 0;
	end if;
	v_counter := v_counter + 1;
	v_id := v_counter;
  SELECT code FROM admin_units.au_level1 INTO v_admin_unit_l1_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT code FROM admin_units.au_level3 INTO v_admin_unit_l3_code WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT fid FROM admin_units.au_khoroolol INTO v_au_khoroolol_id WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT id FROM data_address.st_street_sub INTO v_street_sub_id WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT name || '-' || code FROM data_address.st_street_sub INTO address_streetname WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));
	SELECT id FROM data_address.au_zipcode_area INTO v_au_post_zone_id WHERE ST_COVERS(geometry, ST_PointOnSurface(ST_Makevalid(NEW.geometry)));

-- 	EXECUTE 'SELECT ST_ClosestPoint(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))::geometry(Point,4326) FROM
-- 	   (SELECT
-- 	      ST_PointN(geom, generate_series(1, ST_NPoints(geom)-1)) as sp,
-- 	      ST_PointN(geom, generate_series(2, ST_NPoints(geom)  )) as ep
-- 	    FROM
-- 	      (select st_makevalid((ST_Dump(ST_Boundary(geometry))).geom) as geom from (
-- 		select geometry from data_address.ca_parcel_address
-- 		union all
-- 		select geometry from data_address.ca_building_address
-- 		) parcel, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as b
-- 		where ST_DWithin(parcel.geometry, ST_GeomFromText(b.new_geometry, 4326)::geometry(Point,4326), 0.0006)
-- 	       ) AS linestrings
-- 	    ) AS segments, (select '''||ST_AsText(new_geometry)||'''::text as new_geometry ) as pp
-- 		group by pp.new_geometry, sp,ep
-- 		order by min(st_distance(ST_MakeLine(sp,ep), ST_GeomFromText(pp.new_geometry, 4326))) asc limit 1; ' INTO point_geometry;


	IF (TG_OP = 'INSERT') THEN
		NEW.created_at := now();
		NEW.is_active := true;
    NEW.id := v_id;
	END IF;
-- 	NEW.geometry := point_geometry;
	NEW.au1 := v_admin_unit_l1_code;
	NEW.au2 := v_admin_unit_l2_code;
	NEW.au3 := v_admin_unit_l3_code;
	NEW.khoroolol_id := v_au_khoroolol_id;
	NEW.street_id := v_street_sub_id;
	NEW.address_streetname := address_streetname;
	NEW.zipcode_id := v_au_post_zone_id;
	NEW.updated_at := now();

END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.create_address_parcel()
  OWNER TO geodb_admin;

DROP TRIGGER a_create_address_parcel ON data_address.ca_parcel_address;
CREATE TRIGGER a_create_address_parcel
  BEFORE INSERT OR UPDATE
  ON data_address.ca_parcel_address
  FOR EACH ROW
  EXECUTE PROCEDURE base.create_address_parcel();
