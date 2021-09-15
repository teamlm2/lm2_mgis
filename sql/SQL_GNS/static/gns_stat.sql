select * from data_landuse.ca_landuse_static
where level_type = 1 and (current_year = date_part('year', CURRENT_DATE) or current_year = date_part('year', CURRENT_DATE) - 1)

select s.*, landuse.parent_code from data_landuse.ca_landuse_static s, codelists.cl_landuse_type landuse
where level_type = 2 and s.landuse = landuse.code

insert into data_landuse.ca_landuse_static(landuse, current_year, area_ga, level_type)

select 6, 2020, round(sum(area_m2)/10000/1000, 2), 1 from data_landuse.ca_landuse_type_tbl
where area_m2 is not null and substring(landuse::text, 1, 1) = '6' 
and is_active = true and now() between '1900-01-01'::date and valid_till

--------------

insert into data_landuse.ca_landuse_static(landuse, current_year, area_ga, level_type)

select c.parent_code, 2020, round(sum(area_m2)/10000/1000, 2), 2 from data_landuse.ca_landuse_type_tbl p, codelists.cl_landuse_type c
where area_m2 is not null and p.landuse = c.code and char_length(c.parent_code::text) = 2
and is_active = true and now() between '1900-01-01'::date and valid_till
group by c.parent_code
order by c.parent_code asc

----
insert into data_landuse.ca_landuse_static(landuse, current_year, area_ga, level_type)

select c.code, 2020, round(sum(area_m2)/10000/1000, 2), 3 from data_landuse.ca_landuse_type_tbl p, codelists.cl_landuse_type c
where area_m2 is not null and p.landuse = c.code and char_length(c.code::text) = 4
and is_active = true and now() between '1900-01-01'::date and valid_till
group by c.code
order by c.code asc


---------------level1

select landuse.description, xxx.*, landuse.mobile_icon from (
select row_number() over() as id, case when s1.landuse is null then s2.landuse else s1.landuse end as landuse, s2.current_year before_year, s2.area_ga before_area_ga, s1.current_year, s1.area_ga from 
(select s.* from data_landuse.ca_landuse_static s
where level_type = 1 and current_year = date_part('year', CURRENT_DATE)) s1
full join (select s.* from data_landuse.ca_landuse_static s
where level_type = 1 and current_year = date_part('year', CURRENT_DATE) - 1) s2 on s1.landuse = s2.landuse)xxx, codelists.cl_landuse_type landuse where xxx.landuse = landuse.code order by landuse asc

---------------level2
select landuse.parent_code,landuse.description, xxx.*, landuse.mobile_icon from (
select row_number() over() as id, case when s1.landuse is null then s2.landuse else s1.landuse end as landuse, s2.current_year before_year, s2.area_ga before_area_ga, s1.current_year, s1.area_ga from 
(select s.* from data_landuse.ca_landuse_static s
where level_type = 2 and current_year = date_part('year', CURRENT_DATE)) s1
full join (select s.* from data_landuse.ca_landuse_static s
where level_type = 2 and current_year = date_part('year', CURRENT_DATE) - 1) s2 on s1.landuse = s2.landuse)xxx, codelists.cl_landuse_type landuse 
where xxx.landuse = landuse.code and landuse.parent_code = 1 order by landuse asc
---------------level3
select landuse.parent_code,landuse.description, xxx.*, landuse.mobile_icon from (
select row_number() over() as id, case when s1.landuse is null then s2.landuse else s1.landuse end as landuse, s2.current_year before_year, s2.area_ga before_area_ga, s1.current_year, s1.area_ga from 
(select s.* from data_landuse.ca_landuse_static s
where level_type = 3 and current_year = 2020) s1
full join (select s.* from data_landuse.ca_landuse_static s
where level_type = 3 and current_year = 2020 - 1) s2 on s1.landuse = s2.landuse)xxx, codelists.cl_landuse_type landuse 
where xxx.landuse = landuse.code and landuse.parent_code = 12 order by landuse asc 



