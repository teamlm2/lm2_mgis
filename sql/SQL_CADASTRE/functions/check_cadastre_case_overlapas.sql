-- Function: base.check_cadastre_case_overlapas(geometry)

-- DROP FUNCTION base.check_cadastre_case_overlapas(geometry,text);

CREATE OR REPLACE FUNCTION base.check_cadastre_case_overlapas(IN input_polgyon_geometry geometry, in input_parcels text)
  RETURNS TABLE(mc_type_txt text, mc_type integer, area_type_txt text, is_true boolean, insert_geom geometry, over_geom geometry, parcel_id character varying, au2 character varying, area_m2 double precision) AS
$BODY$

DECLARE
	spa_count integer;
	v_utmsrid integer;
BEGIN 
	RAISE NOTICE 'parcels (%)',  input_parcels;
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

	RETURN query select 'Кадастрын мэдээллийн сан' as mc_type_txt, 1 as mc_type, aa.code::text ||':'|| aa.description as landuse_type, true, dd.geom, cpt.geometry, cpt.parcel_id, cpt.au2, base.calculate_area_utm_decimal(st_intersection(dd.geom, cpt.geometry)) from data_soums_union.ca_parcel_tbl cpt 
			left join codelists.cl_landuse_type aa on cpt.landuse = aa.code
			join (select st_geometrytype(geom), st_srid(geom), geom  from (
			select 
			input_polgyon_geometry as geom
			)xxx) dd on st_overlaps(cpt.geometry, dd.geom) or st_covers(cpt.geometry, dd.geom) or st_covers(dd.geom, cpt.geometry) 
			where now() between cpt.valid_from and cpt.valid_till and cpt.parcel_id not in (select replace(unnest(string_to_array(input_parcels, ',')), ' ', ''))
			union all
			select 'ГЗБТ-н мэдээллийн сан' ||' ('|| ss.short_name ||')' as mc_type_txt, 2 as mc_type, aa.code ||':'|| aa.name as plan_zone_type, cpt.is_active, dd.geom, cpt.polygon_geom, cpt.parcel_id::text, cpt.au2, base.calculate_area_utm_decimal(st_intersection(dd.geom, cpt.polygon_geom)) from data_plan.pl_project_parcel cpt 
			left join data_plan.cl_plan_zone aa on cpt.plan_zone_id = aa.plan_zone_id
			join data_plan.pl_project pp on cpt.project_id = pp.project_id 
			left join data_plan.cl_plan_type ss on pp.plan_type_id = ss.plan_type_id
			join (select st_geometrytype(geom), st_srid(geom), geom  from (
			select 
			input_polgyon_geometry as geom
			)xxx) dd on st_overlaps(cpt.polygon_geom, dd.geom) or st_covers(cpt.polygon_geom, dd.geom) or st_covers(dd.geom, cpt.polygon_geom) 
			where pp.workrule_status_id = 15 and pp.is_active is true and cpt.right_form_id in (2,3,8) and date_part('year', pp.end_date) >= date_part('year', now())
			union all
			select 'UBGIS мэдээллийн сан' as mc_type_txt, 3 as mc_type, aa.code ||':'|| aa.description as landuse_type, true, dd.geom, cpt.geometry, cpt.parcel_id, cpt.au2, base.calculate_area_utm_decimal(st_intersection(dd.geom, cpt.geometry)) from data_ub.ca_ub_parcel_tbl cpt 			
			left join codelists.cl_landuse_type aa on cpt.landuse = aa.code
			join (select st_geometrytype(geom), st_srid(geom), geom  from (
			select 
			input_polgyon_geometry as geom
			)xxx) dd on st_overlaps(cpt.geometry, dd.geom) or st_covers(cpt.geometry, dd.geom) or st_covers(dd.geom, cpt.geometry) 
			where edit_status = 40;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.check_cadastre_case_overlapas(geometry, text)
  OWNER TO geodb_admin;
