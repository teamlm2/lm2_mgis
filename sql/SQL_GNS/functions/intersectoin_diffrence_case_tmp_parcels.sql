-- Function: base.intersectoin_diffrence_case_tmp_parcels(integer)

-- DROP FUNCTION base.intersectoin_diffrence_case_tmp_parcels(bigint);

CREATE OR REPLACE FUNCTION base.intersectoin_diffrence_case_tmp_parcels(
    parcel_id bigint)
  RETURNS integer AS
$BODY$

DECLARE    
    distance text;
    geometry geometry(Polygon,4326);
    landuse integer;
    v_utmsrid integer;
    id text;
    value_array text array;
    is_insert_count = integer;
BEGIN
    IF (parcel_id is  null) THEN
      RAISE exception '%', 'parcel id is null!';
    END IF;
    
    EXECUTE 'select geometry from data_landuse.ca_tmp_landuse_type_tbl where parcel_id = ''' || parcel_id || ''';' INTO geometry;     /* have tried selecting  as well */
    EXECUTE 'select landuse from data_landuse.ca_tmp_landuse_type_tbl where parcel_id = ''' || parcel_id || ''';' INTO landuse;
    IF (geometry is  null) THEN
      RAISE exception '%', 'Geometry is null!';
    END IF;

    IF NOT(st_geometrytype(geometry) = 'ST_Polygon' OR st_geometrytype(geometry) = 'ST_MultiPolygon') THEN
      RAISE exception '%', 'Wrong geometry type';
    END IF;

    SELECT base.find_utm_srid(st_centroid(geometry)) into v_utmsrid;
    IF NOT FOUND THEN
      RAISE EXCEPTION '%','SRID not found';
    END IF;

    IF (geometry IS NOT NULL) THEN			

	EXECUTE 'with new_numbers as (
			WITH gns AS (
				select l.parcel_id, st_makevalid(l.geometry) as geometry from data_landuse.ca_landuse_type_tbl l
				where l.is_active = true and st_intersects(l.geometry, ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326))
				)
			SELECT parcel_id, 
			(ST_DUMP(ST_Difference(
						f.geometry,        
						(
							select (ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326)::geometry(Polygon, 4326))
						)
					))).geom::geometry(Polygon,4326) as geometry
			FROM gns f
		)
		update data_landuse.ca_landuse_type_tbl
		  set is_active = false, valid_till = now(), is_overlaps_historiy = true
		from new_numbers s
		where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id and not st_equals(data_landuse.ca_landuse_type_tbl.geometry, s.geometry);';		

	EXECUTE 'insert into data_landuse.ca_landuse_type_tbl(is_active, landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood, geometry)			
			WITH gns AS (
				select l.parcel_id, st_makevalid(l.geometry) as geometry, l.landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood from data_landuse.ca_landuse_type_tbl l
				where l.is_overlaps_historiy = true and st_intersects(l.geometry, ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326))
				)
			SELECT true, landuse, landuse_level1, landuse_level2, address_khashaa, address_streetname, address_neighbourhood, 
			(ST_DUMP(ST_Difference(
						f.geometry,        
						(
							select (ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326)::geometry(Polygon, 4326))
						)
					))).geom::geometry(Polygon,4326) as geometry
			FROM gns f;';

	EXECUTE 'insert into data_landuse.ca_landuse_type_tbl (is_active, landuse, geometry) values(true, '''||landuse||''', ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326));';

	EXECUTE 'with new_numbers as (
			WITH gns AS (
				select l.parcel_id, st_makevalid(l.geometry) as geometry from data_landuse.ca_landuse_type_tbl l
				where l.is_overlaps_historiy = true and st_intersects(l.geometry, ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326))
				)
			SELECT parcel_id, 
			(ST_DUMP(ST_Difference(
						f.geometry,        
						(
							select (ST_GeomFromText('''||ST_AsText(geometry)||'''::text, 4326)::geometry(Polygon, 4326))
						)
					))).geom::geometry(Polygon,4326) as geometry
			FROM gns f
		)
		update data_landuse.ca_landuse_type_tbl
		  set is_overlaps_historiy = false
		from new_numbers s
		where data_landuse.ca_landuse_type_tbl.parcel_id = s.parcel_id;';	

				
	END IF;
	return landuse;
END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.intersectoin_diffrence_case_tmp_parcels(bigint)
  OWNER TO geodb_admin;

select base.intersectoin_diffrence_case_tmp_parcels(6)

select p.parcel_id, p.is_active, p.area_m2, st_area(p.geometry), st_astext(t.geometry), st_astext(p.geometry)  from data_landuse.ca_tmp_landuse_type_tbl t, data_landuse.ca_landuse_type_tbl p
where st_intersects(p.geometry, t.geometry) and t.parcel_id = 6 order by is_active

select p.* from data_landuse.ca_tmp_landuse_type_tbl t, data_landuse.ca_landuse_type_tbl p
where st_equals(p.geometry, t.geometry) and t.parcel_id = 6 order by is_active

select st_x(st_centroid(t.geometry)), st_x(st_centroid(p.geometry)) from data_landuse.ca_tmp_landuse_type_tbl t, data_landuse.ca_landuse_type_tbl p
where p.is_active = true and st_intersects((t.geometry), (p.geometry)) and t.parcel_id = 5
and base.calculate_area_utm(ST_intersection(t.geometry, p.geometry)) = base.calculate_area_utm(t.geometry) 
and st_x(st_centroid(t.geometry))::text = st_x(st_centroid(p.geometry))::text

select count(p.parcel_id) from data_landuse.ca_tmp_landuse_type_tbl t, data_landuse.ca_landuse_type_tbl p
where p.is_active = true and st_intersects((t.geometry), (p.geometry)) and t.parcel_id = 5
and base.calculate_area_utm(ST_intersection(t.geometry, p.geometry)) = base.calculate_area_utm(t.geometry) 
and st_x(st_centroid(t.geometry))::text = st_x(st_centroid(p.geometry))::text