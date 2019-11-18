CREATE OR REPLACE FUNCTION base.ub_calculate_dem_cama_parcel(dem_type integer, parcel_id text)
  RETURNS double precision AS
$BODY$

DECLARE
    
    dem_value double precision;
    geometry geometry(Polygon,4326);
    v_utmsrid integer;
BEGIN
    IF (parcel_id is  null) THEN
      RAISE exception '%', 'parcel id is null!';
    END IF;
    
    EXECUTE 'select geometry from data_ub.ca_ub_parcel_tbl where parcel_id = ''' || parcel_id || ''';' INTO geometry;     /* have tried selecting * as well */
    
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
    
    EXECUTE 'select val, row_number() over(partition by xxx.parcel_id, 2, True) as rank from ( 
                      select parcel.au2, parcel.parcel_id, (ST_DumpAsPolygons(rast)).geom::geometry, (ST_DumpAsPolygons(rast)).val from ( 
                      select au2, parcel_id, geometry FROM data_ub.ca_ub_parcel_tbl parcel 
                      where parcel.parcel_id = ''' || parcel_id || '''
                      )parcel, data_raster.mongolia_dem rast 
                      where st_intersects(parcel.geometry, rast) and rast.dem_type = '|| dem_type ||'
                      )xxx, (select au2, parcel_id, (geometry) as geometry FROM data_ub.ca_ub_parcel_tbl parcel 
                      where parcel.parcel_id =  ''' || parcel_id || ''') parcel 
                      where parcel.parcel_id = xxx.parcel_id and st_intersects(xxx.geom, parcel.geometry);' INTO dem_value;

    RETURN dem_value;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.ub_calculate_dem_cama_parcel(integer, text)
  OWNER TO geodb_admin;



select base.ub_calculate_dem_cama_parcel(1, '1800900001');

