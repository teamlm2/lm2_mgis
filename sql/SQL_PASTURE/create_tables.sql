set search_path to pasture, codelists;

create table set_nz_pasture_type
(
pasture_type int references codelists.cl_pasture_type on update cascade on delete restrict not null,
natural_zone int references pasture.au_natural_zone on update cascade on delete restrict not null,
current_value decimal not null,
percent_value decimal not null,
duration_begin date NOT NULL DEFAULT now(),
duration_end date NOT NULL DEFAULT now(),
duration_days integer not null,
sheep_unit decimal not null,
unique (pasture_type, natural_zone)
);
grant select, insert, update, delete on set_nz_pasture_type to land_office_administration;
grant select on set_nz_pasture_type to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;

--------------

drop table if exists pasture.ca_point_area cascade;
CREATE TABLE pasture.ca_point_area
(
  id serial PRIMARY KEY,
  point_detail_id varchar(15) references pasture.ps_point_detail on update cascade on delete restrict,
  soil_id text,
  sub_id text,
  soil_name text,
  area_m2 numeric,
  valid_from date DEFAULT ('now'::text)::date,
  valid_till date DEFAULT 'infinity'::date,
  geometry geometry(Polygon,4326),
  au2 varchar(5) references admin_units.au_level2 on update cascade on delete restrict not null
)
WITH (
  OIDS=FALSE
);
ALTER TABLE pasture.ca_point_area
  OWNER TO geodb_admin;
GRANT ALL ON TABLE pasture.ca_point_area TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE pasture.ca_point_area TO contracting_update;
GRANT SELECT ON TABLE pasture.ca_point_area TO contracting_view;
GRANT SELECT ON TABLE pasture.ca_point_area TO reporting;

-- Index: pasture.st_idx_ca_point_area

-- DROP INDEX pasture.st_idx_ca_point_area;

CREATE INDEX st_idx_ca_point_area
  ON pasture.ca_point_area
  USING gist
  (geometry);


-- Trigger: set_default_valid_time on pasture.ca_point_area

-- DROP TRIGGER set_default_valid_time ON pasture.ca_point_area;

CREATE TRIGGER set_default_valid_time
  BEFORE INSERT OR UPDATE
  ON pasture.ca_point_area
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_valid_time();

---

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON pasture.ca_point_area
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON pasture.ca_point_area
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

alter table pasture.ca_point_area alter au2 drop not null;

delete from pasture.ca_point_area;
insert into pasture.ca_point_area(point_detail_id, soil_id, sub_id, soil_name, geometry)

select point_detail_id, soil_id, sub_id, soil_name, geom from (
select row_number() over(partition by aa.gid) as rank, mm.point_detail_id, soil_id, sub_id, soil_name, ((st_dump(geom)).geom) as geom from public.point_area aa
left join pasture.ca_pasture_monitoring m on st_within(m.geometry, aa.geom)
left join pasture.ps_point_detail_points mm on m.point_id = mm.point_id
)xxx where rank = 1

--------------------

select xxx.soil_id, xxx.sub_id, xxx.soil_name, geom from (
select soil_id, sub_id, soil_name, ((st_dump(geom)).geom) as geom from public.point_area aa
)xxx, pasture.ca_point_area bb
 where not st_equals(xxx.geom, bb.geometry)

insert into pasture.ca_point_area(soil_id, sub_id, soil_name, geometry)
select soil_id, sub_id, soil_name, ((st_dump(geom)).geom) as geom from public.point_area aa, pasture.ca_point_area bb
where not st_equals(aa.geometry, bb.geometry)

