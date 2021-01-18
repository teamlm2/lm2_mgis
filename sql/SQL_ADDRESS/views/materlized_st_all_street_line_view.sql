-- View: data_address.st_mat_street_line_view

-- DROP MATERIALIZED VIEW data_address.st_mat_street_line_view cascade;

CREATE MATERIALIZED VIEW data_address.st_mat_street_line_view AS 
 SELECT row_number() OVER () AS id,
    s.id AS street_id,
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
    s.au2,
    s.valid_till,
    s.valid_from,
    r.geometry AS geometry
   FROM data_address.st_street s
     JOIN data_address.cl_street_type st ON s.street_type_id = st.code
     LEFT JOIN data_plan.cl_plan_decision_level dl ON s.decision_level_id = dl.plan_decision_level_id
     JOIN ( SELECT row_number() OVER () AS gid,
            (st_multi(st_union(st_road.line_geom)))::geometry(MultiLineString,4326) AS geometry,
            st_road.street_id
           FROM data_address.st_road
          WHERE st_road.street_id IS NOT NULL
          GROUP BY st_road.street_id) r ON s.id = r.street_id
  WHERE s.is_active = true;

ALTER TABLE data_address.st_mat_street_line_view
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_address.st_mat_street_line_view TO geodb_admin;
GRANT SELECT ON TABLE data_address.st_mat_street_line_view TO reporting;
GRANT SELECT ON TABLE data_address.st_mat_street_line_view TO land_office_administration;
GRANT INSERT, DELETE ON TABLE data_address.st_mat_street_line_view TO cadastre_view;
GRANT INSERT, DELETE ON TABLE data_address.st_mat_street_line_view TO db_creation;
GRANT UPDATE, INSERT, DELETE ON TABLE data_address.st_mat_street_line_view TO cadastre_update;
