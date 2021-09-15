-- Function: base.dynamic_pivot(text, text)

-- DROP FUNCTION base.dynamic_pivot(text, text);

CREATE OR REPLACE FUNCTION base.dynamic_pivot(
    central_query text,
    headers_query text)
  RETURNS refcursor AS
$BODY$
DECLARE
  left_column text;
left_column1 text;
  header_column text;
  value_column text;
  h_value text;
  headers_clause text;
  query text;
  j json;
  r record;
  curs refcursor := 'mycursor';
  i int:=1;
BEGIN
  -- find the column names of the source query
  EXECUTE 'select row_to_json(_r.*) from (' ||  central_query || ') AS _r' into j;
  FOR r in SELECT * FROM json_each_text(j)
  LOOP
    IF (i=1) THEN left_column := r.key;
      ELSEIF (i=2) THEN left_column1 := r.key;
ELSEIF (i=3) THEN header_column := r.key;
      ELSEIF (i=4) THEN value_column := r.key;
    END IF;
    i := i+1;
  END LOOP;

  --  build the dynamic transposition query (based on the canonical model)
  FOR h_value in EXECUTE headers_query
  LOOP
    headers_clause := concat(headers_clause,
     format(chr(10)||',min(case when %I=%L then %I::text end) as %I',
           header_column,
	   h_value,
	   value_column,
	   h_value ));
  END LOOP;

  query := format('SELECT %I, %I %s FROM (select *,row_number() over() as rn from (%s) AS _c) as _d GROUP BY '||left_column||', '||left_column1||' order by min(rn)',
           left_column,
left_column1,
	   headers_clause,
	   central_query,
	   left_column);

  -- open the cursor so the caller can FETCH right away
  OPEN curs FOR execute query;
  RETURN curs;
END 
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.dynamic_pivot(text, text)
  OWNER TO geodb_admin;
