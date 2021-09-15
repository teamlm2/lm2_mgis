select geometry from data_soums_union.ca_parcel_tbl where au2 = '01125' and (valid_till = 'infinity' or valid_till is null)

CREATE OR REPLACE VIEW data_landuse.clip_to_gns_test AS 
WITH forest AS (
    select parcel_id, st_makevalid(geometry) as geometry from data_landuse.ca_landuse_type_tbl where au2 = '01125' and (valid_till = 'infinity' or valid_till is null) --limit 1000
    ),
    lake AS (
    select parcel_id, st_makevalid(geometry) as geometry from data_soums_union.ca_parcel_tbl where au2 = '01125' and (valid_till = 'infinity' or valid_till is null)
    )
SELECT parcel_id, 
        ST_Difference(
            f.geometry,
            /* Correlated subquery to fetch only the lakes intersected by the current forest */
            (
                SELECT ST_Union(l.geometry) 
                FROM lake l 
                WHERE ST_Intersects(l.geometry,f.geometry)
            )
        )
FROM forest f;
ALTER TABLE data_landuse.clip_to_gns_test
  OWNER TO geodb_admin;