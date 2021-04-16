﻿alter table data_address.st_entrance disable trigger a_create_address_entry_id;

insert into data_address.st_entrance(entrance_id, type, geometry)
select 590577+row_number() over(), 1, geom from data_address_cd.bgd_entry

where gid >0 and gid <= 5000

---and geom in (select geometry from data_address.st_entrance)

SELECT max(entrance_id::int) FROM data_address.st_entrance

select entrance_id, substring(au2, 1, 3) from data_address.st_entrance
where substring(au2, 1, 3) = '011'
limit 100

delete from data_address.st_entrance where substring(au2, 1, 3) = '011'