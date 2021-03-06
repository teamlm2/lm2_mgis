﻿--set search_path to codelists, settings, public;
drop table if exists data_plan.cl_au_dispute_status cascade;
create table data_plan.cl_au_dispute_status
(
code int primary key,
description varchar(75) unique not null,
description_en varchar(75) unique
);
grant select, insert, update, delete on data_plan.cl_au_dispute_status to land_office_administration;
grant select on data_plan.cl_au_dispute_status to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;
COMMENT ON TABLE data_plan.cl_au_dispute_status
  IS 'Хилийн цэсийн маргааны явц';
  
insert into data_plan.cl_au_dispute_status values (1,'явц-1','1');
insert into data_plan.cl_au_dispute_status values (2,'явц-2','2');
insert into data_plan.cl_au_dispute_status values (3,'явц-3','3');
insert into data_plan.cl_au_dispute_status values (4,'явц-4','4');

drop table if exists data_plan.cl_au_dispute_form cascade;
create table data_plan.cl_au_dispute_form
(
code int primary key,
description varchar(75) unique not null,
description_en varchar(75) unique
);
grant select, insert, update, delete on data_plan.cl_au_dispute_form to land_office_administration;
grant select on data_plan.cl_au_dispute_form to cadastre_view, cadastre_update, contracting_view, contracting_update, reporting;
COMMENT ON TABLE data_plan.cl_au_dispute_form
  IS 'Хилийн цэсийн маргааны явц';
  
insert into data_plan.cl_au_dispute_form values (1,'Зохиомол','1');
insert into data_plan.cl_au_dispute_form values (2,'Бодит','2');

drop table if exists admin_units.au_base_dispute cascade;
create table admin_units.au_base_dispute
(
id serial primary key,
dispute_form_code int references data_plan.cl_au_dispute_form on update cascade on delete cascade,
level_type int REFERENCES codelists.cl_au_level_type on update cascade on delete cascade,
au_base_level_id int,
land_location text,
dispute_reason text,
description text,
created_by integer,
updated_by integer,
created_at timestamp without time zone NOT NULL DEFAULT now(),
updated_at timestamp without time zone NOT NULL DEFAULT now()
);
grant select, insert, update, delete on admin_units.au_base_dispute to contracting_update;
grant select on admin_units.au_base_dispute to contracting_view, reporting;

drop table if exists admin_units.au_base_dispute_status cascade;
create table admin_units.au_base_dispute_status
(
id serial primary key,
au_base_dispute_id int references admin_units.au_base_dispute on update cascade on delete cascade,
status int REFERENCES data_plan.cl_au_dispute_status on update cascade on delete cascade,
status_date timestamp without time zone NOT NULL DEFAULT now(),
description text,
created_by integer,
updated_by integer,
created_at timestamp without time zone NOT NULL DEFAULT now(),
updated_at timestamp without time zone NOT NULL DEFAULT now()
);
grant select, insert, update, delete on admin_units.au_base_dispute_status to contracting_update;
grant select on admin_units.au_base_dispute_status to contracting_view, reporting;
