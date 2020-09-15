WITH ap AS (
         SELECT point_1.entrance_id AS gid, point_1.geometry AS geom FROM (select * from data_address.st_entrance where parcel_id = 846699) point_1
        ), street AS (SELECT line_1.line_geom AS geom FROM (select geometry as line_geom from data_address.st_all_street_line_view where id = 62978) as line_1
        ), cp AS (SELECT a.gid AS ap_id, a.geom AS ap,
st_setsrid(st_addpoint(st_makeline(a.geom, st_closestpoint(b.geom, a.geom)), st_translate(a.geom, sin(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision, cos(st_azimuth(a.geom, st_closestpoint(b.geom, a.geom))) * st_distance(a.geom, st_closestpoint(b.geom, a.geom)) * 1.01::double precision)), 4326) AS vec,
st_setsrid(st_addpoint(st_linemerge(b.geom), st_translate(st_pointn(st_linemerge(b.geom), '-2'::integer), sin(st_azimuth(st_pointn(st_linemerge(b.geom), '-2'::integer), st_pointn(st_linemerge(b.geom), '-1'::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), '-1'::integer), st_pointn(st_linemerge(b.geom), '-2'::integer)) * 1.1::double precision), cos(st_azimuth(st_pointn(st_linemerge(b.geom), '-2'::integer), st_pointn(st_linemerge(b.geom), '-1'::integer))) * (st_distance(st_pointn(st_linemerge(b.geom), '-1'::integer), st_pointn(st_linemerge(b.geom), '-2'::integer)) * 1.1::double precision))), 4326) AS line
           FROM ap a
             LEFT JOIN street b ON st_dwithin(st_setsrid(b.geom, 4326), st_setsrid(a.geom, 4326), 25::double precision)
          ORDER BY a.gid, (st_distance(b.geom, a.geom))
        )
 SELECT st_linecrossingdirection(cp.line, cp.vec) AS side, st_intersection(cp.vec, cp.line) as intersect_point FROM cp;


select * from data_address.st_entrance where parcel_id = 846699
select geometry as line_geom from data_address.st_all_street_line_view where id = 62978

select * from data_address.st_street_point where street_id = 62978