DROP TABLE if exists data_address.all_street_point cascade;

CREATE TABLE data_address.all_street_point
(
  id int NOT NULL,
  gudamj_gid integer,
  geometry geometry(Point,4326),
  CONSTRAINT all_street_point_pkey PRIMARY KEY (id),
  CONSTRAINT all_street_point_gudamj_gid_fkey FOREIGN KEY (gudamj_gid)
      REFERENCES data_address.all_gudamj (gid) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE RESTRICT
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_address.all_street_point
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.all_street_point TO geodb_admin;
GRANT SELECT ON TABLE data_address.all_street_point TO reporting;
GRANT SELECT ON TABLE data_address.all_street_point TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.all_street_point TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.all_street_point TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.all_street_point TO cadastre_update;

------

DROP VIEW if exists data_address.geocad_street_point_view;

CREATE OR REPLACE VIEW data_address.geocad_street_point_view AS 
 SELECT *
   FROM data_address.all_street_point s
  WHERE st_intersects(( SELECT au_level2.geometry
           FROM admin_units.au_level2
          WHERE au_level2.code::text = (( SELECT set_role_user.working_au_level2::text AS au2
                   FROM settings.set_role_user
                  WHERE set_role_user.user_name::name = "current_user"() AND set_role_user.is_active = true))), s.geometry);

ALTER TABLE data_address.geocad_street_point_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.geocad_street_point_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.geocad_street_point_view TO reporting;
GRANT SELECT ON TABLE data_address.geocad_street_point_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.geocad_street_point_view TO cadastre_update;

----

set search_path to data_address;



-- DROP FUNCTION base.all_street_point_id();

CREATE OR REPLACE FUNCTION base.all_street_point_id()
  RETURNS trigger AS
$BODY$
DECLARE
  entrance_id int;
  v_counter int;
BEGIN

	NEW.geometry := st_force2d(NEW.geometry);

 IF (NEW.geometry IS NOT NULL) THEN

	execute 'SELECT max(id::int) FROM data_address.all_street_point' into v_counter;

	if v_counter is null then
		v_counter := 0;
	end if;
	v_counter := v_counter + 1;
	entrance_id := v_counter;

	IF (TG_OP = 'INSERT') THEN
		NEW.id := entrance_id;
	END IF;	
	

END IF;

    RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION base.all_street_point_id()
  OWNER TO geodb_admin;
	
--DROP TRIGGER a_all_street_point_id ON data_address.all_street_point;	
CREATE TRIGGER a_all_street_point_id
  BEFORE INSERT OR UPDATE
  ON data_address.all_street_point
  FOR EACH ROW
  EXECUTE PROCEDURE base.all_street_point_id();