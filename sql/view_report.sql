select a.*, f.name, parcel.au2 from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id
where parcel.au2 = '01125'
order by a.parcel_id
limit 100

--------------

SELECT parcel_id,
       json_object_agg(name, factor_value ORDER BY name)
   FROM (
     select a.parcel_id, f.name, a.factor_value from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id
--GROUP BY a.parcel_id, name
order by a.parcel_id

limit 100
   ) s
  GROUP BY parcel_id
  ORDER BY parcel_id;

------------

CREATE FUNCTION base.dynamic_pivot(central_query text, headers_query text)
 RETURNS refcursor AS
$$
DECLARE
  left_column text;
  header_column text;
  value_column text;
  h_value text;
  headers_clause text;
  query text;
  j json;
  r record;
  curs refcursor;
  i int:=1;
BEGIN
  -- find the column names of the source query
  EXECUTE 'select row_to_json(_r.*) from (' ||  central_query || ') AS _r' into j;
  FOR r in SELECT * FROM json_each_text(j)
  LOOP
    IF (i=1) THEN left_column := r.key;
      ELSEIF (i=2) THEN header_column := r.key;
      ELSEIF (i=3) THEN value_column := r.key;
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

  query := format('SELECT %I %s FROM (select *,row_number() over() as rn from (%s) AS _c) as _d GROUP BY %I order by min(rn)',
           left_column,
	   headers_clause,
	   central_query,
	   left_column);

  -- open the cursor so the caller can FETCH right away
  OPEN curs FOR execute query;
  RETURN curs;
END 
$$ LANGUAGE plpgsql;

---------------

BEGIN;
 
   SELECT base.dynamic_pivot(
       'select a.parcel_id, f.name, a.factor_value from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id 
where parcel.au2 = '''||'01125'||''' order by a.parcel_id ', 'select DISTINCT f.name from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id
order by 1'
     ) AS cur;

FETCH ALL FROM "mycursor";

COMMIT;