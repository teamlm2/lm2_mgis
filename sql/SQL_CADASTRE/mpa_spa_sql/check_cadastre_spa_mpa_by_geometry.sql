-- Function: base.check_cadastre_spa_mpa_by_geometry(integer, geometry, geometry, geometry, integer)

-- DROP FUNCTION base.check_cadastre_spa_mpa_by_geometry(integer, geometry, geometry, geometry, integer);

CREATE OR REPLACE FUNCTION base.check_cadastre_spa_mpa_by_geometry(
    IN input_polgyon_geometry geometry)
  RETURNS integer AS
$BODY$

DECLARE
	spa_count integer;
	v_utmsrid integer;
BEGIN 
    
	IF (input_polgyon_geometry is null) THEN
	  RAISE exception '%', 'Polygon Geometry is null!';
	END IF;

	IF NOT(st_geometrytype(input_polgyon_geometry) = 'ST_Polygon' OR st_geometrytype(input_polgyon_geometry) = 'ST_MultiPolygon') THEN
		RAISE exception '%', 'Wrong geometry type. Only polygon';
	END IF;

	SELECT base.find_utm_srid(st_centroid(input_polgyon_geometry)) into v_utmsrid;
	IF NOT FOUND THEN
	  RAISE EXCEPTION '%','SRID not found';
	END IF;

	execute 'select count(a.parcel_id) from (
			select * from data_soums_union.ca_spa_parcel_tbl p
			join codelists.cl_landuse_type clt on p.landuse = clt.code
			where clt.code2 = 61
			) as a,
			(select $1 as geom) b
			where st_intersects(a.geometry, b.geom) ' into spa_count USING input_polgyon_geometry;

		return spa_count;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.check_cadastre_spa_mpa_by_geometry(geometry)
  OWNER TO geodb_admin;

select base.check_cadastre_spa_mpa_by_geometry(st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326));
