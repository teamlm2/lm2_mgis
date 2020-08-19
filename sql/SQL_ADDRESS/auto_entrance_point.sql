select ST_MakeLine(cp_pt_line, cp_line_pt) from (
SELECT (ST_ClosestPoint(pt,line)) AS cp_pt_line,
	(ST_ClosestPoint(line,pt)) As cp_line_pt
FROM (SELECT (select st_centroid(geometry) from data_address.ca_parcel_address
where id = 419488) As pt,
		(select s.geometry from data_address.ca_parcel_address p, data_address.st_all_street_line_view s
where p.id = 419488
group by s.geometry
order by min(st_distance(p.geometry, s.geometry)) asc limit 1) As line
	) As foo
)xxx;