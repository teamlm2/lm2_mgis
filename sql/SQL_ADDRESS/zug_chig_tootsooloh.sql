SELECT
   degrees(ST_Azimuth(ST_ClosestPoint(l.line_geom,p.geometry), p.geometry)) AS azimuth, p.id
FROM data_address.st_road l, data_address.st_street_point_test p where l.id = 870

SELECT
   degrees(ST_Azimuth(ST_ClosestPoint(l.line_geom,p.geometry), p.geometry)) AS azimuth, p.id
FROM data_address.st_road l, data_address.st_street_point_test p where l.id = 1978

SELECT degrees(ST_Azimuth(ST_Point(25, 45), ST_Point(75, 100))) AS degA_B,
	    degrees(ST_Azimuth(ST_Point(75, 100), ST_Point(25, 45))) AS degB_A;

select degrees(ST_Azimuth(st_centroid(h.vec), st_centroid(h.seg)))
from (
    select 
        ST_MakeLine(cp.p, point.geometry) vec,
        ST_MakeLine(cp.p, 
            ST_LineInterpolatePoint(
                line.line_geom, 
                ST_LineLocatePoint(line.line_geom, cp.p) * 1.01) 
        ) seg
        from (
            select ST_ClosestPoint(line.line_geom, point.geometry) as p from data_address.st_street_point_test point, data_address.st_road line where line.id = 1978
        )cp, data_address.st_street_point_test point, data_address.st_road line where line.id = 1978
    ) as h