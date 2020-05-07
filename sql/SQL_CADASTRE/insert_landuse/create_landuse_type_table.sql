DROP TABLE if exists data_landuse.ca_landuse_type_tbl;
CREATE TABLE data_landuse.ca_landuse_type_tbl
(
  parcel_id serial NOT NULL,
  is_active boolean not null DEFAULT false,
  landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
  landuse_level1 int references codelists.cl_landuse_type on update cascade on delete restrict,
  landuse_level2 int references codelists.cl_landuse_type on update cascade on delete restrict,
  area_m2 numeric,
  address_khashaa character varying(64),
  address_streetname character varying(250),
  address_neighbourhood character varying(250),
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  au1 character varying(3) references admin_units.au_level1 on update cascade on delete restrict,
  au2 character varying(5) references admin_units.au_level2 on update cascade on delete restrict,
  au3 character varying(8) references admin_units.au_level3 on update cascade on delete restrict,
  created_by integer,
  updated_by integer,
  created_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  updated_at timestamp(0) without time zone NOT NULL DEFAULT now(),
  CONSTRAINT ca_landuse_type_tbl_pkey PRIMARY KEY (parcel_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_type_tbl
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_type_tbl TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_type_tbl TO cadastre_update;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_tbl TO cadastre_view;
GRANT SELECT ON TABLE data_landuse.ca_landuse_type_tbl TO reporting;

-- Index: data_landuse.idx_ca_landuse_type_landuse

-- DROP INDEX data_landuse.idx_ca_landuse_type_landuse;

CREATE INDEX idx_ca_landuse_type_landuse
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (landuse);

-- Index: data_landuse.idx_ca_landuse_type_parcel_id

-- DROP INDEX data_landuse.idx_ca_landuse_type_parcel_id;

CREATE INDEX idx_ca_landuse_type_parcel_id
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (parcel_id);

-- Index: data_landuse.idx_ca_landuse_type_valid_from

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_from;

CREATE INDEX idx_ca_landuse_type_valid_from
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (valid_from);

-- Index: data_landuse.idx_ca_landuse_type_valid_till

-- DROP INDEX data_landuse.idx_ca_landuse_type_valid_till;

CREATE INDEX idx_ca_landuse_type_valid_till
  ON data_landuse.ca_landuse_type_tbl
  USING btree
  (valid_till);

-- Index: data_landuse.st_idx_ca_landuse_type_tbl

-- DROP INDEX data_landuse.st_idx_ca_landuse_type_tbl;

CREATE INDEX st_idx_ca_landuse_type_tbl
  ON data_landuse.ca_landuse_type_tbl
  USING gist
  (geometry);


-- Trigger: set_default_valid_time on data_landuse.ca_landuse_type_tbl

-- DROP TRIGGER set_default_valid_time ON data_landuse.ca_landuse_type_tbl;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

-- Trigger: update_area on data_landuse.ca_landuse_type_tbl

-- DROP TRIGGER update_area ON data_landuse.ca_landuse_type_tbl;

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_landuse.ca_landuse_type_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();