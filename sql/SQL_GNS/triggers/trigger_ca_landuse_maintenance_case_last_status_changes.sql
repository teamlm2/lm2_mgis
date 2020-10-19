CREATE OR REPLACE FUNCTION base.ca_landuse_maintenance_case_last_status_changes()
  RETURNS trigger AS
$BODY$
BEGIN        
        if (TG_OP = 'INSERT') THEN
                EXECUTE 'update data_landuse.ca_landuse_maintenance_case set status_id = ' || NEW.status || 'where id =' || NEW.case_id;
        ELSIF (TG_OP = 'DELETE') THEN
                EXECUTE 'update data_landuse.ca_landuse_maintenance_case set status_id = (select status_id from data_landuse.ca_landuse_maintenance_status
                                                                                        where case_id = '|| OLD.case_id ||'
                                                                                        group by case_id, status_id, id
                                                                                        order by id desc limit 1) where case_id =' || OLD.case_id;
        END IF;
        RETURN NULL;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE SECURITY DEFINER
  COST 100;
ALTER FUNCTION base.ca_landuse_maintenance_case_last_status_changes()
  OWNER TO geodb_admin;