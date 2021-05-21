DROP FUNCTION base.line_extend_straight(text);
CREATE OR REPLACE FUNCTION base.line_extend_straight(
    line_geom text)
  RETURNS geometry AS
$BODY$

DECLARE
        extend_line_geom geometry(LineString,4326);
BEGIN

execute 'SELECT
st_setsrid(ST_Reverse((SELECT ST_MakeLine(ST_TRANSLATE(a, sin(az1) * len, cos(az1) * len), ST_TRANSLATE(b,sin(az2) * len, cos(az2) * len))
  FROM (
    SELECT a, b, ST_Azimuth(a,b) AS az1, ST_Azimuth(b, a) AS az2, ST_Distance(a,b) + 0.0000000001 AS len
      FROM (
        SELECT ST_StartPoint(the_geom) AS a, ST_EndPoint(the_geom) AS b
          FROM  ST_GeomFromText($1) AS the_geom
    ) AS sub
) AS sub2)),4326)' into extend_line_geom USING  line_geom;

return extend_line_geom;

END;

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.line_extend_straight(text)
  OWNER TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.line_extend_straight(text) TO public;
GRANT EXECUTE ON FUNCTION base.line_extend_straight(text) TO geodb_admin;
GRANT EXECUTE ON FUNCTION base.line_extend_straight(text) TO application_update;

select * from base.line_extend_straight('LINESTRING(106.927732827008 47.923098771691,106.927128609398 47.926381148771,106.927128609398 47.926381148771)')