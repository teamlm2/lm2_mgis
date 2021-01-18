-- Function: base.update_street_geometry()

-- DROP FUNCTION base.update_street_geometry();

CREATE OR REPLACE FUNCTION base.update_street_geometry()
  RETURNS trigger AS
$BODY$
DECLARE
  v_id int;
new_geometry geometry(MultiLineString,4326);
BEGIN
	
	--insert
	IF (NEW.street_id IS NOT NULL) THEN
		RAISE NOTICE 'insert x (%)',  NEW.street_id;		
		execute 'SELECT st_multi(st_union(r.line_geom))::geometry(MultiLineString,4326) AS geometry FROM data_address.st_road r WHERE r.street_id = ''' || NEW.street_id || ''' GROUP BY r.street_id ' into new_geometry ;
	
		--RAISE NOTICE 'geom x (%)', new_geometry;
		execute 'update data_address.st_street set line_geom = st_setsrid(ST_GeomFromText('''||ST_AsText(new_geometry)||'''), 4326) where id = ''' || NEW.street_id || '''';
		--NEW.street_id = NEW.street_id;

	--delete
	ELSIF (NEW.street_id IS NULL) THEN
		IF (OLD.street_id IS NOT NULL) THEN
		RAISE NOTICE 'delete x (%)',  old.street_id;		
		execute 'SELECT st_multi(st_union(r.line_geom))::geometry(MultiLineString,4326) AS geometry FROM data_address.st_road r WHERE r.id != ''' || OLD.id || ''' and r.street_id = ''' || OLD.street_id || ''' GROUP BY r.street_id ' into new_geometry ; 
		execute 'update data_address.st_street set line_geom = st_setsrid(ST_GeomFromText('''||ST_AsText(new_geometry)||'''), 4326) where id = ''' || OLD.street_id || '''';
		--NEW.street_id = null;
		END IF;
	END IF;
	
	NEW.street_id := NEW.street_id;
    RETURN new;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.update_street_geometry()
  OWNER TO geodb_admin;


CREATE TRIGGER a_update_street_geometry
  BEFORE INSERT OR UPDATE
  ON data_address.st_road
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_street_geometry();

------------
update data_address.st_road set street_id = null where id = 474575;
update data_address.st_road set street_id = 128888 where id = 474575;


with new_numbers as (
	SELECT r.street_id, st_multi(st_union(r.line_geom))::geometry(MultiLineString,4326) AS geometry FROM data_address.st_road r
	WHERE r.street_id = 128888
	GROUP BY r.street_id
	)
	update data_address.st_street set line_geom = p.geometry
	from new_numbers p
	where data_address.st_street.id = p.street_id