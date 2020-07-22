set search_path to data_landuse, public;
drop table if exists set_overlaps_landuse cascade;
create table set_overlaps_landuse
(
  in_landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
  ch_landuse int references codelists.cl_landuse_type on update cascade on delete restrict,
  is_input_landuse boolean not null,
  is_safety_zone boolean not null,
  constraint set_overlaps_landuse_pkey PRIMARY KEY (in_landuse, ch_landuse)
);
grant select, insert, update, delete on set_overlaps_landuse to land_office_administration;
grant select, insert, update, delete on set_overlaps_landuse to cadastre_update, contracting_update;
grant select on set_overlaps_landuse to cadastre_view, contracting_view, reporting;

insert into set_overlaps_landuse(in_landuse, ch_landuse, is_input_landuse) values (3411, 2204, false);
insert into set_overlaps_landuse(in_landuse, ch_landuse, is_input_landuse) values (3411, 2205, false);
insert into set_overlaps_landuse(in_landuse, ch_landuse, is_input_landuse) values (3411, 2206, false);
