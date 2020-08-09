delete from data_address.st_street;
insert into data_address.st_street(name, is_active, in_source, street_type_id, geometry)

select street, true, 1, 1, geom from data_address.aa_gudamj_1984_multi1;

---------------------
delete from data_address.st_street_sub;
insert into data_address.st_street_sub(code, name, is_active, in_source, street_type_id, geometry)

select number, street, true, 1, 1, (ST_DUMP(geom)).geom::geometry(Polygon,4326) AS geometry from data_address.aa_gudamj_1984_1;

---------------update

select s.name, l.street_name, split_part(l.street_name, ' ', 1) from data_address.st_street s
join data_address.aa_ub_street_list l on s.name = l.street_name

WITH s AS (
select s.id, s.name, l.street_name, l.decision_no, l.decision_date, l.level_id, l.description, l.urt from data_address.st_street s
join data_address.aa_ub_street_list l on s.name = l.street_name
)
UPDATE data_address.st_street
SET description = s.description, 
decision_no = s.decision_no, 
decision_level_id = s.level_id, 
decision_date = s.decision_date,
length = s.urt
from s 
where data_address.st_street.id = s.id;

---------------
WITH s AS (
select s.id, s.name, l.street_name, l.decision_no, l.decision_date, l.level_id, l.description, l.urt from data_address.st_street s
join data_address.aa_ub_street_list l on s.name ilike '%'||l.street_name||'%'

where s.id not in (select id from data_address.st_street where decision_no is not null)
)
UPDATE data_address.st_street
SET description = s.description, 
decision_no = s.decision_no, 
decision_level_id = s.level_id, 
decision_date = s.decision_date,
length = s.urt
from s 
where data_address.st_street.id = s.id;

---------------
WITH s AS (
select s.id, s.name, l.street_name, l.decision_no, l.decision_date, l.level_id, l.description, l.urt from data_address.st_street s
join data_address.aa_ub_street_list l on l.street_name ilike s.name||'%'

where s.id not in (select id from data_address.st_street where decision_no is not null)
)
UPDATE data_address.st_street
SET description = s.description, 
decision_no = s.decision_no, 
decision_level_id = s.level_id, 
decision_date = s.decision_date,
length = s.urt
from s 
where data_address.st_street.id = s.id;

---------------
WITH s AS (
select s.id, s.name, l.street_name, l.decision_no, l.decision_date, l.level_id, l.description, l.urt from data_address.st_street s, data_address.aa_ub_street_list l
WHERE SIMILARITY(name, split_part(l.street_name, ' ', 1)) > 0.4 and s.decision_no is null
)
UPDATE data_address.st_street
SET description = s.description, 
decision_no = s.decision_no, 
decision_level_id = s.level_id, 
decision_date = s.decision_date,
length = s.urt
from s 
where data_address.st_street.id = s.id;


--*****************

select SIMILARITY(name,l.street_name), s.name, l.street_name, split_part(l.street_name, ' ', 1) from data_address.st_street s, data_address.aa_ub_street_list l
WHERE SIMILARITY(name,l.street_name) > 1 and s.id not in (select id from data_address.st_street where decision_no is not null);

select * from data_address.st_street

select s.name, l.street_name, split_part(l.street_name, ' ', 1) from data_address.st_street s
join data_address.aa_ub_street_list l on s.name like split_part(l.street_name, ' ', 1)||'%'
where s.id not in (select id from data_address.st_street where decision_no is not null)

select s.name, l.street_name, split_part(l.street_name, ' ', 1) from data_address.st_street s
join data_address.aa_ub_street_list l on l.street_name ilike s.name||'%'

where s.id not in (select id from data_address.st_street where decision_no is not null)
select * from data_address.st_street where decision_no is null

