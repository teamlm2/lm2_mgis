select count(lcode3) from public.gns1;


insert into data_landuse.ca_landuse_type_tbl (landuse_level1, landuse_level2, landuse, geometry)

select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns1

select lcode2 from public.gns1
where lcode2 not in (select code from codelists.cl_landuse_type);

select lcode3 from public.gns1
where lcode3 not in (select code from codelists.cl_landuse_type);

select lcode2, lcode3 from public.gns1
where lcode2 = 46

update public.gns1 set lcode2 = 41 where lcode2 = 46

---------------

select count(lcode3) from public.gns2;

insert into data_landuse.ca_landuse_type_tbl (landuse_level1, landuse_level2, landuse, geometry)

select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns2


select lcode2 from public.gns2
where lcode2 not in (select code from codelists.cl_landuse_type);

select lcode3 from public.gns2
where lcode3 not in (select code from codelists.cl_landuse_type) group by lcode3;

select lcode2, lcode3, substring(lcode3::text, 1, 2)::int from public.gns2
where lcode2 = 27

update public.gns2 set lcode2 = substring(lcode3::text, 1, 2)::int where lcode3 = 220400

update public.gns2 set lcode3 = 2205 where lcode3 in (2100
,2606
,2207
,2211
,2208
)

insert into codelists.cl_landuse_type(code, description, code2, description2, fill_color, boundary_color, boundary_width, parent_code) values (2120, 'Барилга байгууламжийн бусад газар', 21, 'Барилга байгууламжийн бусад газар', '#737373', '#828282', 1, 21);

--------------------

delete from data_landuse.ca_landuse_type_tbl;
insert into data_landuse.ca_landuse_type_tbl (landuse_level1, landuse_level2, landuse, geometry)


select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns1
union all
select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns2
union all
select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns3
union all
select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns4
union all
select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns5
union all
select substring(lcode3::text, 1, 1)::int, lcode2, lcode3, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geom from public.gns6