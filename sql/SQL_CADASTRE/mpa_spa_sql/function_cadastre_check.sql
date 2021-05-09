select ST_AsGeoJSON(geometry) from data_soums_union.ca_parcel_tbl cpt 
where parcel_id = '1781110810'

------------

select a.parcel_id, a.geometry from (
select * from data_soums_union.ca_spa_parcel_tbl p
join codelists.cl_landuse_type clt on p.landuse = clt.code
where clt.code2 = 61
) as a,
(select st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326) as geom) b
where st_intersects(a.geometry, b.geom)

----------------

select a.parcel_id, a.geometry from (
select * from data_soums_union.ca_spa_parcel_tbl p
join codelists.cl_landuse_type clt on p.landuse = clt.code
where clt.code2 = 61
) as a,
(select st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[100.68792742693,50.642687536191],[100.77234943774,50.632307780763],
[100.75366587797,50.513286585196],[100.65817212803,50.515362536281],[100.68792742693,50.642687536191]]]}'), 4326) as geom) b
where st_intersects(a.geometry, b.geom)

-------------

select a.* from (
select * from admin_units.au_mpa_zone p
--join codelists.cl_landuse_type clt on p.landuse = clt.code
--where clt.code2 = 61
) as a,
(select st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326) as geom) b
where st_intersects(a.geometry, b.geom)

-----------
select p.parcel_id, cst.description spa_desc, clt.description mpa_desc, p.spa_land_name, b.zone_type_name::text, smza.description allow_desc, smza.allow_type, smzal.landuse landuse_code, clt1.description as landuse_desc from (
select st_setsrid(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[106.824989114693,47.8629835583944],[106.825450480659,47.8613542873159],[106.820461126449,47.8606443743848],[106.81993612855,47.8622203086864],[106.824989114693,47.8629835583944]]]}'), 4326) as geom
) as a
join data_soums_union.ca_spa_parcel_tbl p on st_intersects(p.geometry, a.geom)
join admin_units.au_mpa_zone b on st_intersects(b.geometry, a.geom)
join codelists.cl_landuse_type clt on p.landuse = clt.code
join codelists.cl_spa_type cst on p.spa_type = cst.code 
left join data_landuse.set_mpa_zone_allow_zone bb on b.zone_type = bb.mpa_zone_type_id
left join data_landuse.st_mpa_zone_allow smza on bb.mpa_zone_allow_id = smza.id 
left join data_landuse.set_mpa_zone_allow_landuse smzal on smzal.mpa_zone_allow_id = smza.id 
left join codelists.cl_landuse_type clt1 on smzal.landuse = clt1.code
where clt.code2 = 61 and cst.code = 1

