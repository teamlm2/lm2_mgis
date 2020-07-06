set search_path to data_landuse, codelists, admin_units, public;

create table set_buffer_au2_landuse
(
  landuse integer references cl_landuse_type on update cascade on delete restrict not null,
  au2 varchar(5) references au_level2 on update cascade on delete restrict not null,
  buffer_value numeric,
  constraint set_buffer_au2_landuse_pkey PRIMARY KEY (landuse, au2)
);
grant select, insert, update, delete on set_buffer_au2_landuse to land_office_administration;
grant select on set_buffer_au2_landuse to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;