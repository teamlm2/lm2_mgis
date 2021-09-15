alter table codelists.cl_landuse_type add column code1 int references codelists.cl_landuse_type on update cascade on delete restrict;

update codelists.cl_landuse_type set code1 = substring(code::text, 1, 1)::int where substring(code::text, 1, 1)::int != 7 and substring(code::text, 1, 1)::int != 9;

select substring(code::text, 1, 1)::int from codelists.cl_landuse_type where substring(code::text, 1, 1)::int != 7 and substring(code::text, 1, 1)::int != 9;