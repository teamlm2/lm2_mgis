set search_path to data_landuse, codelists, admin_units, public;

drop table if exists set_buffer_au2_landuse cascade;
create table set_buffer_au2_landuse
(
  landuse integer references cl_landuse_type on update cascade on delete restrict not null,
  au2 varchar(5) references au_level2 on update cascade on delete restrict not null,
  buffer_value numeric,
  description text,
  constraint set_buffer_au2_landuse_pkey PRIMARY KEY (landuse, au2)
);
grant select, insert, update, delete on set_buffer_au2_landuse to land_office_administration;
grant select on set_buffer_au2_landuse to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;

-----
drop table if exists set_buffer_parcel cascade;
create table set_buffer_parcel
(
  id serial PRIMARY KEY,
  parcel_id text,
  parcel_type integer references codelists.cl_parcel_type on update cascade on delete restrict not null,
  buffer_value numeric,
  description text
);
grant select, insert, update, delete on set_buffer_parcel to land_office_administration;
grant select, insert, update, delete on set_buffer_parcel to cadastre_update, contracting_update;
grant select on set_buffer_parcel to cadastre_view, contracting_view, reporting;

