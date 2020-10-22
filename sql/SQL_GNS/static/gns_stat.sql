select * from data_landuse.ca_landuse_static
where level_type = 1 and (current_year = date_part('year', CURRENT_DATE) or current_year = date_part('year', CURRENT_DATE) - 1)

select s.*, landuse.parent_code from data_landuse.ca_landuse_static s, codelists.cl_landuse_type landuse
where level_type = 2 and s.landuse = landuse.code

insert into data_landuse.ca_landuse_static(landuse, current_year, area_ga, level_type)

select 6, 2020, round(sum(area_m2)/10000/1000, 2), 1 from data_landuse.ca_landuse_type_tbl
where area_m2 is not null and substring(landuse::text, 1, 1) = '6' 
and is_active = true and now() between '1900-01-01'::date and valid_till


select landuse.description, xxx.* from (
select row_number() over() as id, case when s1.landuse is null then s2.landuse else s1.landuse end as landuse, s2.current_year before_year, s2.area_ga before_area_ga, s1.current_year, s1.area_ga from 
(select s.* from data_landuse.ca_landuse_static s
where level_type = 1 and current_year = date_part('year', CURRENT_DATE)) s1
full join (select s.* from data_landuse.ca_landuse_static s
where level_type = 1 and current_year = date_part('year', CURRENT_DATE) - 1) s2 on s1.landuse = s2.landuse)xxx, codelists.cl_landuse_type landuse where xxx.landuse = landuse.code

-----
select landuse.parent_code,landuse.description, xxx.* from (
select row_number() over() as id, case when s1.landuse is null then s2.landuse else s1.landuse end as landuse, s2.current_year before_year, s2.area_ga before_area_ga, s1.current_year, s1.area_ga from 
(select s.* from data_landuse.ca_landuse_static s
where level_type = 2 and current_year = date_part('year', CURRENT_DATE)) s1
full join (select s.* from data_landuse.ca_landuse_static s
where level_type = 2 and current_year = date_part('year', CURRENT_DATE) - 1) s2 on s1.landuse = s2.landuse)xxx, codelists.cl_landuse_type landuse where xxx.landuse = landuse.code



