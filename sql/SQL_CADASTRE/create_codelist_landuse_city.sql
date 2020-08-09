drop table if exists codelists.cl_landuse_type_city;
CREATE TABLE codelists.cl_landuse_type_city
(
  code integer NOT NULL,
  description character varying(256) NOT NULL,
  description_en character varying(256),
  fill_color character varying(7) DEFAULT NULL::character varying,
  boundary_color character varying(7) DEFAULT NULL::character varying,
  boundary_width numeric,
  parent_code int references codelists.cl_landuse_type on update cascade on delete restrict,
  CONSTRAINT cl_landuse_type_city_pkey PRIMARY KEY (code)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_landuse_type_city
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_landuse_type_city TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_landuse_type_city TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_landuse_type_city TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_landuse_type_city TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_landuse_type_city TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_landuse_type_city TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_landuse_type_city TO reporting;
COMMENT ON TABLE codelists.cl_landuse_type_city
  IS 'ХОТ ТОСГОН, БУСАД СУУРИН ГАЗРЫН ГАЗАР АШИГЛАЛТЫН ЗОРИУЛАЛТЫН АНГИЛАЛ';

delete from codelists.cl_landuse_type_city;
insert INTO codelists.cl_landuse_type_city(code, description, parent_code, fill_color, boundary_color, boundary_width)
select lcode4, desc4, lcode3, '#fff0a6', '#828282', 1 from public."Sheet1" 

select desc3, lcode3 from public."Sheet1" 
where lcode3 not in (select code from codelists.cl_landuse_type)

insert into codelists.cl_landuse_type(code, description, code2, fill_color, boundary_color, boundary_width, parent_code)
select lcode3, desc3, substring(lcode3::text, 1, 2)::int, '#fff0a6', '#828282', 1, substring(lcode3::text, 1, 2)::int from public."Sheet1" 
where lcode3 not in (select code from codelists.cl_landuse_type);

--------------

insert into codelists.cl_landuse_type(code, description, code2, fill_color, boundary_color, boundary_width, parent_code)
select lcode4, desc4, lcode3, '#fff0a6', '#828282', 1, lcode3 from public."Sheet1" 
where lcode4 not in (select code from codelists.cl_landuse_type);

select * from codelists.cl_landuse_type

update public."Sheet1" set lcode3 = substring(lcode4::text, 1, 4)::int where lcode3 is null;