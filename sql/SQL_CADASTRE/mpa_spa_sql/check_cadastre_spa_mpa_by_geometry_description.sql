-- Function: base.check_cadastre_spa_mpa_by_geometry_description(geometry)

-- DROP FUNCTION base.check_cadastre_spa_mpa_by_geometry_description(geometry);

CREATE OR REPLACE FUNCTION base.check_cadastre_spa_mpa_by_geometry_description(
    IN input_polgyon_geometry geometry)
  RETURNS TABLE(parcel_id text, spa_desc text, mpa_desc text, spa_land_name text, zone_type_name text, allow_desc text, allow_type integer, landuse_code integer, landuse_desc text) AS
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

	RETURN query select p.parcel_id::text, cst.description::text spa_desc, clt.description::text mpa_desc, p.spa_land_name::text, b.zone_type_name::text, smza.description::text allow_desc, smza.allow_type, smzal.landuse landuse_code, clt1.description::text as landuse_desc from (
			select input_polgyon_geometry as geom
			) as a
			join data_soums_union.ca_spa_parcel_tbl p on st_intersects(p.geometry, a.geom)
			join admin_units.au_mpa_zone b on st_intersects(b.geometry, a.geom)
			join codelists.cl_landuse_type clt on p.landuse = clt.code
			join codelists.cl_spa_type cst on p.spa_type = cst.code 
			left join data_landuse.set_mpa_zone_allow_zone bb on b.zone_type = bb.mpa_zone_type_id
			left join data_landuse.st_mpa_zone_allow smza on bb.mpa_zone_allow_id = smza.id 
			left join data_landuse.set_mpa_zone_allow_landuse smzal on smzal.mpa_zone_allow_id = smza.id 
			left join codelists.cl_landuse_type clt1 on smzal.landuse = clt1.code
			where clt.code2 = 61 and cst.code = 1;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.check_cadastre_spa_mpa_by_geometry_description(geometry)
  OWNER TO geodb_admin;

select * from base.check_cadastre_spa_mpa_by_geometry_description(st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326));
