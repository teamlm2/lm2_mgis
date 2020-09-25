CREATE OR REPLACE FUNCTION base.application_landuse_changes()
  RETURNS trigger AS
$BODY$
BEGIN        
        if (TG_OP = 'UPDATR') THEN
                EXECUTE 'update data_soums_union.ct_application set status_id = ' || NEW.approved_landuse || ' where app_id =' || NEW.application;
        END IF;
        RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.application_landuse_changes()
  OWNER TO geodb_admin;