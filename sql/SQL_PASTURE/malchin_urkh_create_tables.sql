drop table if exists pasture.ps_person_group_livestock;
CREATE TABLE pasture.ps_person_group_livestock
(
  person_group integer references data_soums_union.ct_person_group on update cascade on delete restrict NOT NULL,
  live_stock_type integer references pasture.cl_livestock on update cascade on delete restrict NOT NULL,
  current_year integer,
  current_value numeric,
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone DEFAULT now(),
  updated_at timestamp(0) without time zone DEFAULT now(),
  PRIMARY KEY (person_group, live_stock_type, current_year)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pasture.ps_person_group_livestock
  OWNER TO geodb_admin;
GRANT ALL ON TABLE pasture.ps_person_group_livestock TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE pasture.ps_person_group_livestock TO contracting_update;
GRANT SELECT ON TABLE pasture.ps_person_group_livestock TO contracting_view;
GRANT SELECT ON TABLE pasture.ps_person_group_livestock TO reporting;

---------------

drop table if exists pasture.ps_person_group_location;
CREATE TABLE pasture.ps_person_group_location
(
  id serial PRIMARY KEY,
  person_group integer references data_soums_union.ct_person_group on update cascade on delete restrict NOT NULL,
  pasture_type integer references codelists.cl_pasture_type on update cascade on delete restrict NOT NULL,
  current_year integer,
  geometry geometry(Point,4326),
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone DEFAULT now(),
  updated_at timestamp(0) without time zone DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pasture.ps_person_group_location
  OWNER TO geodb_admin;
GRANT ALL ON TABLE pasture.ps_person_group_location TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE pasture.ps_person_group_location TO contracting_update;
GRANT SELECT ON TABLE pasture.ps_person_group_location TO contracting_view;
GRANT SELECT ON TABLE pasture.ps_person_group_location TO reporting;

----------------------
drop table if exists pasture.ps_person_group_location_livestock;
CREATE TABLE pasture.ps_person_group_location_livestock
(
  id serial PRIMARY KEY,
  person_group_location_id integer references pasture.ps_person_group_location on update cascade on delete restrict NOT NULL,
  live_stock_type integer references pasture.cl_livestock on update cascade on delete restrict NOT NULL,
  current_value numeric,
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone DEFAULT now(),
  updated_at timestamp(0) without time zone DEFAULT now(),
  unique (person_group_location_id, live_stock_type)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pasture.ps_person_group_location_livestock
  OWNER TO geodb_admin;
GRANT ALL ON TABLE pasture.ps_person_group_location_livestock TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE pasture.ps_person_group_location_livestock TO contracting_update;
GRANT SELECT ON TABLE pasture.ps_person_group_location_livestock TO contracting_view;
GRANT SELECT ON TABLE pasture.ps_person_group_location_livestock TO reporting;