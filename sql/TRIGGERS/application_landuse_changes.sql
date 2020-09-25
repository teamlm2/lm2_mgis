CREATE OR REPLACE FUNCTION base.application_landuse_changes()
  RETURNS trigger AS
$BODY$
BEGIN        
        if (TG_OP = 'UPDATE') THEN
                EXECUTE 'update data_soums_union.ct_application set approved_landuse = ' || NEW.landuse || ' where app_id =(select app_id from data_soums_union.ct_application
																where parcel = '''|| NEW.parcel_id::text ||''' order by app_timestamp desc limit 1)';
        END IF;
        RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.application_landuse_changes()
  OWNER TO geodb_admin;

CREATE TRIGGER app_landuse_changes
  AFTER INSERT OR UPDATE OR DELETE
  ON data_soums_union.ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.application_landuse_changes();

select * from data_soums_union.ct_application
where parcel = '6105300849' order by app_timestamp desc limit 1

'|| OLD.application ||'