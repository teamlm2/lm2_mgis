select ST_MakeLine(cp_pt_line, cp_line_pt) 
	from (
		SELECT (ST_ClosestPoint(pt,line)) AS cp_pt_line,
			(ST_ClosestPoint(line,pt)) As cp_line_pt
			FROM (SELECT (select st_centroid(geometry) from data_address.ca_parcel_address
				where id = 1674166) As pt,
						(select s.geometry from data_address.ca_parcel_address p, data_address.st_all_street_line_view s
				where p.id = 1674166
				group by s.geometry
				order by min(st_distance(p.geometry, s.geometry)) asc limit 1) As line
				) As foo
	)xxx;


select aa.gid, p.parcel_id from (
SELECT row_number() over() gid, ST_SRID(t.geom) ,t.geom, ST_GeomFromText(ST_AsText(t.geom)) l_geom, gs.*, ST_AsText(line.geom) AS line
FROM ST_Boundary(((select (geometry) from data_address.ca_parcel_address where id = 1650472))) AS t(geom)
CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(x)
CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, x), ST_PointN(geom, x+1)) AS line(geom)
) aa, data_address.ca_parcel_address p
where st_touches(ST_PointOnSurface(aa.geom),(p.geometry));

CREATE OR REPLACE VIEW data_address.test AS 
SELECT row_number() over() gid, ST_SRID(t.geom) ,t.geom, ST_GeomFromText(ST_AsText(t.geom)) l_geom, gs.*, ST_AsText(line.geom) AS line
FROM ST_Boundary(((select (geometry) from data_address.ca_parcel_address where id = 1650472))) AS t(geom)
CROSS JOIN LATERAL generate_series(1, ST_NPoints(geom) - 1)AS gs(x)
CROSS JOIN LATERAL ST_MakeLine(ST_PointN(geom, x), ST_PointN(geom, x+1)) AS line(geom);

ALTER TABLE data_address.test
  OWNER TO geodb_admin;