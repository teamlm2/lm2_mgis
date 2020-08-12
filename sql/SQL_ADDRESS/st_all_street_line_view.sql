CREATE OR REPLACE VIEW data_address.st_all_street_line_view AS 
 SELECT s.id,
    s.code,
    s.name,
    s.description,
    s.decision_date,
    s.decision_no,
    s.decision_level_id,
    dl.description AS decision_level_desc,
    s.is_active,
    s.street_type_id,
    st.description AS street_type_desc,
    s.length,
    r.geometry::geometry(MultiLineString,4326) AS geometry
   FROM data_address.st_street s
     JOIN data_address.cl_street_type st ON s.street_type_id = st.code
     LEFT JOIN data_plan.cl_plan_decision_level dl ON s.decision_level_id = dl.plan_decision_level_id
     JOIN ( SELECT row_number() OVER () AS gid,
            st_union(st_multi(st_road.line_geom)) AS geometry,
            st_road.street_id
           FROM data_address.st_road
          WHERE st_road.street_id IS NOT NULL
          GROUP BY st_road.street_id) r ON s.id = r.street_id;

ALTER TABLE data_address.st_all_street_line_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_all_street_line_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_all_street_line_view TO reporting;
GRANT SELECT ON TABLE data_address.st_all_street_line_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_all_street_line_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_all_street_line_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_all_street_line_view TO cadastre_update;