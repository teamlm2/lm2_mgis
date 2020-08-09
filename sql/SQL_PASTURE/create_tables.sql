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