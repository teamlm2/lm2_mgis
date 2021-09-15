--delete from data_monitoring.mt_monitoring_point_value where attribute_id = 115;

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'slope'), p.slope, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.slope 
order by monitoring_point_map_id

--------------

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'gumus'), p.gumus, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.gumus 
order by monitoring_point_map_id

--------------

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'ph'), p.ph, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.ph 
order by monitoring_point_map_id

--------------

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'n_id'), p.n_id, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.n_id 
order by monitoring_point_map_id


--------------

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'absorb'), p.absorb, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.absorb 
order by monitoring_point_map_id


--------------

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value, condition_attribute_id, condition_attribute_lov_value_id)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'infra_id'), p.infra_id, 79, 61  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.infra_id 
order by monitoring_point_map_id

--------------soil index
--------------soil_id

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_id'), 
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 1) )
from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------soil_comp

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_comp'),
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 2))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------soil_form

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_form'),
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 3))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------soil_mech

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_mech'),
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 4))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------soil_type

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_type'),
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 5))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------so_st_na

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'so_st_na'), 
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 6))
from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------soil_rock

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'soil_rock'), 
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 7))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------wind_eros

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'wind_eros'),
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 8))
 from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

--------------wat_eros

insert into data_monitoring.mt_monitoring_point_value(monitoring_point_map_id, attribute_id, value)

select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'wind_eros'), 
(select attribute_lov_value_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 9))
from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id



select d.monitoring_point_map_id, (select attribute_id from data_monitoring.mt_cl_attribute where attribute_name = 'wat_eros'), p.soil_ind, SPLIT_PART(p.soil_ind, ' ', 5)  from data_monitoring.aa_tarailan_point_2018 p
join data_monitoring.mt_monitor_point m on p.convert_id = m.convert_id
join data_monitoring.mt_monitoring_point_map d on m.monitor_point_id = m.monitor_point_id
where m.convert_id is not null
group by d.monitoring_point_map_id, p.soil_ind 
order by monitoring_point_map_id

update data_monitoring.aa_tarailan_point_2018 set soil_ind = REPLACE(soil_ind, '  ', ' ' )


(select attribute_value_result_id from data_monitoring.mt_cl_attribute_lov_value where code = SPLIT_PART(p.soil_ind, ' ', 10) )

select * from data_monitoring.mt_cl_attribute where attribute_name = 'soil_id'