-- Function: base.gn_parcel_auto_numbering(geometry)

-- DROP FUNCTION base.gn_parcel_auto_numbering(geometry);

CREATE OR REPLACE FUNCTION base.gn_parcel_auto_numbering(IN input_polgyon_geometry geometry)
  RETURNS TABLE(geo_id text, geo_name text, gn_geo geometry, distance numeric) AS
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

	RETURN query select b.geo_id::text, b.documentname::text, b.geo_data, min(st_distance(a.geometry, b.geo_data))::numeric 
			from 
			(select input_polgyon_geometry as geometry) a, 
			data_address_import.gn_soft b
			group by b.geo_id, b.documentname, b.geo_data
			order by min(st_distance(a.geometry, b.geo_data)) limit 1;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100
  ROWS 1000;
ALTER FUNCTION base.gn_parcel_auto_numbering(geometry)
  OWNER TO geodb_admin;
  

select geometry, ST_AsGeoJSON(geometry) as geometry from data_address.ca_parcel_address a
where parcel_id = '8116000542' 

select * from base.gn_parcel_auto_numbering
(st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326));


select b.geo_id, b.documentname, b.geo_data, min(st_distance(a.geometry, b.geo_data)) 
from 
(select (select geometry from data_address.ca_parcel_address where parcel_id = '8116000542')) a, 
data_address_import.gn_soft b
group by b.geo_id, b.documentname, b.geo_data
order by min(st_distance(a.geometry, b.geo_data)) limit 1


