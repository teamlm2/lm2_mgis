insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'GFID'), bb.parcel_id, aa.gfid  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'chiglel'), bb.parcel_id, aa.chiglel  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.chiglel is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'gaz_add'), bb.parcel_id, aa.gazner  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.gazner is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hariuc_hun'), bb.parcel_id, aa.hariutshun  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.hariutshun is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hugtsaa_guits'), bb.parcel_id, 2024  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'shaltgaan'), bb.parcel_id, aa.ner  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.ner is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;

----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'TXT'), bb.parcel_id, aa.txt  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.txt is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'l_use_rate'), bb.parcel_id, aa.huchinchad  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.huchinchad is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;
----------
insert into data_plan.pl_project_parcel_attribute_value(attribute_id, parcel_id, attribute_value)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'HuchChadl'), bb.parcel_id, aa.huchinchad  from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1 and aa.huchinchad is not null
ON CONFLICT (attribute_id, parcel_id) 
DO NOTHING;




select aa.* from data_plan.aa_uls_single_point aa
join data_plan.pl_project_parcel bb on st_equals(aa.geom, bb.point_geom)
where bb.project_id = 1

select * from data_plan.pl_project_parcel
where point_geom is not null and project_id = 1


select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'l_use_rate'

update data_plan.aa_uls_single_point set gazner = ner where gazner = 'U_M';
update data_plan.aa_uls_single_point set gazner = txt where gazner is null;
