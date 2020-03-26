SET SEARCH_PATH TO pasture, admin_units, public;

drop table if exists cl_rc_change;
CREATE TABLE cl_rc_change
(
  code int NOT NULL primary key,
  description character varying(500) NOT NULL,
  description2 character varying(500) NOT NULL
);
grant select, insert, update, delete on cl_rc_change to address_admin;
grant select on cl_rc_change to address_view;
COMMENT ON TABLE cl_rc_change
  IS 'Бэлчээрийн өөрчлөлтийн жагсаалт';

insert into pasture.cl_rc_change values (1, '1.Зохистой ашиглалт бүхий бэлчээр', '1.Соргог бэлчээр');
insert into pasture.cl_rc_change values (2, '2.Зохистой ашиглалтаар сайжруулж буй бэлчээр', '2.Сайжирч буй бэлчээр');
insert into pasture.cl_rc_change values (3, '3.Ашиглалтын хэлбэрийг өөрчлөх шаардлагатай бэлчээр', '3.Доройтож буй бэлчээр');

drop table if exists set_rc_change;
CREATE TABLE set_rc_change
(
  id serial primary key,
  rc_change_id int references cl_rc_change on update cascade on delete restrict,
  value character varying(500) NOT NULL
);
grant select, insert, update, delete on set_rc_change to address_admin;
grant select on set_rc_change to address_view;
COMMENT ON TABLE set_rc_change
  IS 'Бэлчээрийн өөрчлөлтийн тохиргоо';

insert into pasture.set_rc_change values (1,  1, '1-1');
insert into pasture.set_rc_change values (2,  1, '1-2');
insert into pasture.set_rc_change values (3,  1, '2-1');
insert into pasture.set_rc_change values (4,  1, '2-2');
insert into pasture.set_rc_change values (5,  1, '3-1');
insert into pasture.set_rc_change values (6,  1, '4-1');

insert into pasture.set_rc_change values (7, 2, '3-2');
insert into pasture.set_rc_change values (8, 2, '3-3');
insert into pasture.set_rc_change values (9, 2, '4-2');
insert into pasture.set_rc_change values (10, 2, '4-3');

insert into pasture.set_rc_change values (11, 3, '1-3');
insert into pasture.set_rc_change values (12, 3, '1-4');
insert into pasture.set_rc_change values (13, 3, '2-3');
insert into pasture.set_rc_change values (14, 3, '3-4');
insert into pasture.set_rc_change values (15, 3, '4-4');
