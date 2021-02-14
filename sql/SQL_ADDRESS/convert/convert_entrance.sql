insert into data_address.st_entrance(type, geometry)
select 1, geom from data_address_cd.bzd_entry

where gid >5000 and gid <= 10000

---and geom in (select geometry from data_address.st_entrance)