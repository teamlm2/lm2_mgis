insert into data_plan.pl_project_parcel(plan_zone_id, landuse, project_id, polygon_geom, gazner, txt, badedturl, is_active, valid_till, end_date)

select (select plan_zone_id from data_plan.cl_plan_zone where code = '21502003'), 26, 1, geom, gaz_add, txt, plan_code, true, exp_date, exp_date  from data_plan.aa_ashiglalt
where plan_code = '21502003';

insert into data_plan.pl_project_parcel(plan_zone_id, landuse, project_id, polygon_geom, gazner, txt, badedturl, is_active, valid_till, end_date)

select (select plan_zone_id from data_plan.cl_plan_zone where code = '21502001'), 26, 1, geom, gaz_add, txt, plan_code, true, exp_date, exp_date  from data_plan.aa_ashiglalt
where plan_code = '21502001';
--group by plan_code

insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'GFID'), bb.parcel_id, aa.gfid  from data_plan.aa_ashiglalt aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.polygon_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

--------------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hugatsaa_ash'), bb.parcel_id, date_part('year', exp_date)  from data_plan.aa_ashiglalt aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.polygon_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

----------

select plan_zone_id from data_plan.cl_plan_zone where code = '21502003'
select plan_zone_id from data_plan.cl_plan_zone where code = '21502001'

select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hugatsaa_ash'

select * from data_plan.cl_attribute_zone where description = 'Гэрээгээр ашиглах хугацаа'


select * from data_plan.aa_ashiglalt

update data_plan.pl_project_parcel set plan_zone_id = 677 where badedturl = '21502001';

select * from data_plan.pl_project_parcel where badedturl = '21502001'