insert into data_plan.cl_attribute_zone (attribute_id, attribute_name, attribute_name_mn, is_active, attribute_group_id, attribute_type, description) 
values (600, 'in_source', 'in_source', true, 1, 'text', 'эх сурвалж')
ON CONFLICT (attribute_id) 
DO NOTHING;
insert into data_plan.cl_attribute_zone (attribute_id, attribute_name, attribute_name_mn, is_active, attribute_group_id, attribute_type, description) 
values (601, 'cur_level', 'cur_level', true, 1, 'text', 'одоогийн түвшин')
ON CONFLICT (attribute_id) 
DO NOTHING;
insert into data_plan.cl_attribute_zone (attribute_id, attribute_name, attribute_name_mn, is_active, attribute_group_id, attribute_type, description) 
values (602, 'fut_level', 'fut_level', true, 1, 'text', 'хүрэх түвшин')
ON CONFLICT (attribute_id) 
DO NOTHING;

select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'metainfo' limit 1;

update data_plan.cl_attribute_zone set attribute_name = 'hariuc_hun', attribute_name_mn = 'hariuc_hun' where attribute_name = 'hariutsah_hun';
update data_plan.cl_attribute_zone set attribute_name = 'metainfo', attribute_name_mn = 'metainfo' where attribute_name = 'METAINFO';


--hurung_hem
--hariutsah_hun hariuc_hun
--METAINFO

--delete from data_plan.set_plan_zone_attribute where plan_type_id != 9;
----------

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hurung_hem' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

----------
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hariuc_hun' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

----------
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'metainfo' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

---------
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select 600, plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

----------
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select 601, plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

----------
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select 602, plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

----------default set attribute
insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'gaz_add' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'GFID' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'hariuc_hun' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'shaltgaan' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'TXT' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'HuchChadl' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'chiglel' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
where code like '30%'
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;

insert into data_plan.set_plan_zone_attribute(attribute_id, plan_zone_id, is_required, plan_type_id)

select (select attribute_id from data_plan.cl_attribute_zone where attribute_name = 'urt' limit 1), plan_zone_id, false, 1 as plan_type from data_plan.cl_plan_zone
where code like '30%'
ON CONFLICT (attribute_id, plan_zone_id, plan_type_id) 
DO NOTHING;