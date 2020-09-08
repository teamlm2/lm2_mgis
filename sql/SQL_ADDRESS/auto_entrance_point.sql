insert into data_address.st_entrance(type, geometry)

select 1, xxx.geom from (
select xxx.* from (
SELECT row_number() over() gid, st_centroid(line.geom) as geom
FROM ST_Boundary(((select ((geometry)) from data_address.ca_parcel_address where id = 1305436))) AS t(geom)
CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(x)
CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, x), ST_PointN(geom, x+1)) AS line(geom)
)xxx
where gid not in ( 
select aa.gid from (
SELECT row_number() over() gid, ST_SRID(line.geom) ,st_centroid(line.geom) as geom
FROM ST_Boundary(((select ((geometry)) from data_address.ca_parcel_address where id = 1305436))) AS t(geom)
CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(x)
CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, x), ST_PointN(geom, x+1)) AS line(geom)
) aa, (select p.parcel_id, d.parcel_id, d.geometry from data_address.ca_parcel_address p, data_address.ca_parcel_address d where p.id = 1305436 and st_touches(p.geometry, d.geometry) and now() between d.valid_from and d.valid_till) p
where st_intersects((aa.geom),(st_buffer(p.geometry, 0.000001)))) 
)xxx, data_address.st_all_street_line_view line
group by xxx.gid, xxx.geom
order by min(st_distance(line.geometry, xxx.geom)) asc limit 1;


(select 
ST_LineMerge((st_dump(line.geometry)).geom) as geometry, line.id
from data_address.st_all_street_line_view line) line
--------------

CREATE OR REPLACE VIEW data_address.test AS 
SELECT row_number() over() gid, ST_SRID(line.geom) ,line.geom, ST_GeomFromText(ST_AsText(t.geom)) l_geom, gs.*, ST_AsText(line.geom) AS line
FROM ST_Boundary(((select ((geometry)) from data_address.ca_parcel_address where id = 1305436))) AS t(geom)
CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(x)
CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, x), ST_PointN(geom, x+1)) AS line(geom);

ALTER TABLE data_address.test
  OWNER TO geodb_admin;

select * from data_address.ca_parcel_address 
where parcel_id = '4201002196'