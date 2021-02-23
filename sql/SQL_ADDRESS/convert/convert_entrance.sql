alter table data_address.st_entrance disable trigger a_create_address_entry_id;

insert into data_address.st_entrance(entrance_id, type, geometry)
select 157288+row_number() over(), 1, geom from data_address_cd.bzd_entry

where gid >20000 and gid <= 25000

---and geom in (select geometry from data_address.st_entrance)

SELECT max(entrance_id::int) FROM data_address.st_entrance