CREATE OR REPLACE FUNCTION base.set_default_au2_line()
  RETURNS trigger AS
$BODY$
DECLARE
  v_admin_unit_l2_code text;

BEGIN
	
 IF (NEW.line_geom IS NOT NULL) THEN
        
	SELECT code FROM admin_units.au_level2 INTO v_admin_unit_l2_code WHERE ST_Within(ST_Centroid(ST_Transform(NEW.line_geom::geography::geometry, base.find_utm_srid(st_centroid(geometry)))), ST_Transform(geometry::geography::geometry, base.find_utm_srid(st_centroid(geometry))));
		
	NEW.au2 := v_admin_unit_l2_code;
 END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.set_default_au2_line()
  OWNER TO geodb_admin;
