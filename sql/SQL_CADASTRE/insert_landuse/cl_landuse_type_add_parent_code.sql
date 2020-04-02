alter table codelists.cl_landuse_type add column parent_code int;

update codelists.cl_landuse_type set parent_code = substring(code::text,1,1)::int;
update codelists.cl_landuse_type set parent_code = 6 where code = 7001;