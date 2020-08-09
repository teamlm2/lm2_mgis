alter table data_plan.aa_haiguul add column plan_code varchar(8);

update data_plan.aa_haiguul set plan_code = '21502001' where txt = 'Төлөвлөсөн УТХГазартай давхацсан';
update data_plan.aa_haiguul set plan_code = '21502001' where txt = 'Одоогийн УТХГазартай давхацсан';

update data_plan.aa_haiguul set plan_code = '21502003' where txt != 'Одоогийн УТХГазартай давхацсан' and txt != 'Төлөвлөсөн УТХГазартай давхацсан';


insert into data_plan.pl_project_parcel(plan_zone_id, landuse, project_id, polygon_geom, gazner, txt, badedturl, is_active, valid_till, end_date)

select (select plan_zone_id from data_plan.cl_plan_zone where code = '21502003'), 26, 1, geom, gaz_add, txt, plan_code, true, exp_date, exp_date  from data_plan.aa_haiguul
where plan_code = '21502003';

insert into data_plan.pl_project_parcel(plan_zone_id, landuse, project_id, polygon_geom, gazner, txt, badedturl, is_active, valid_till, end_date)

select (select plan_zone_id from data_plan.cl_plan_zone where code = '21502001'), 26, 1, geom, gaz_add, txt, plan_code, true, exp_date, exp_date  from data_plan.aa_haiguul
where plan_code = '21502001';
--group by plan_code

insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'GFID'), bb.parcel_id, 'АМ хайгуулын тусгай зөвшөөрөл'  from data_plan.aa_haiguul aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.polygon_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

--------------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'on'), bb.parcel_id, date_part('year', grant_date)  from data_plan.aa_haiguul aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.polygon_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

-----------

insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'TXT'), bb.parcel_id, aa.txt  from data_plan.aa_haiguul aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.polygon_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

----------

select plan_zone_id from data_plan.cl_plan_zone where code = '21502003'
select plan_zone_id from data_plan.cl_plan_zone where code = '21502001'

select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'gaz_add'

select * from data_plan.cl_attribute_zone where description = 'Гэрээгээр ашиглах хугацаа'


select * from data_plan.aa_haiguul

update data_plan.pl_project_parcel set plan_zone_id = 677 where badedturl = '21502001';

select * from data_plan.pl_project_parcel where badedturl = '21502001'