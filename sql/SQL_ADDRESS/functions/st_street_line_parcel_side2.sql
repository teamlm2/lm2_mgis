start_line_x start_line_y
entry_intersects_x entry_intersects_y
end_line_x end_line_y
entry_point_x entry_point_y

str_id
parcel_id


SELECT
	ST_LineCrossingDirection(foo.line1, foo.line2) As l1_cross_l2 --,
	--ST_LineCrossingDirection(foo.line2, foo.line1) As l2_cross_l1
FROM (
 SELECT
  ST_GeomFromText('LINESTRING(start_line_x start_line_y, entry_intersects_x entry_intersects_y, end_line_x end_line_y)') As line2,
  ST_GeomFromText('LINESTRING(start_line_x start_line_y, entry_intersects_x entry_intersects_y, entry_point_x entry_point_y)') As line1
  ) As foo;

----------

SELECT
	ST_LineCrossingDirection(foo.line1, foo.line2) As l1_cross_l2 --,
	--ST_LineCrossingDirection(foo.line2, foo.line1) As l2_cross_l1
FROM (
 SELECT
  ST_GeomFromText('LINESTRING(108.416787158867 46.3358094239678, 108.41678715972 46.3393020080482, 108.417721727751 46.3410167363241)') As line2,
  ST_GeomFromText('LINESTRING(108.416787158867 46.3358094239678, 108.41678715972 46.3393020080482, 108.418717939009 46.3381773504626)') As line1
  ) As foo;