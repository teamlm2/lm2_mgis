set search_path to data_landuse, codelists;

DROP TABLE if exists  data_landuse.cl_landsue_movement_status cascade;
CREATE TABLE cl_landsue_movement_status
(
  code integer NOT NULL primary key,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75),
  is_confirm boolean,
  is_draft boolean
);
grant select, insert, update, delete on cl_landsue_movement_status to address_admin;
grant select on cl_landsue_movement_status to address_view;
grant select on cl_landsue_movement_status to address_view, cadastre_view;
COMMENT ON TABLE cl_landsue_movement_status
  IS 'Нэгдмэл сангийн шилжилт хөдөлгөөний төлөв';

insert into data_landuse.cl_landsue_movement_status values (1, 'Үндэслэл', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (2, 'Дүгнэлт', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (3, 'Зураг бэлтгэх', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (4, 'Санал авах', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (5, 'ГНС-н өөрчлөлтийн төсөлд оруулах', null, false, true);
insert into data_landuse.cl_landsue_movement_status values (6, 'Засгийн газарт хүргүүлэх', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (7, 'Засгийн газраас буцаасан', null, false, false);
insert into data_landuse.cl_landsue_movement_status values (8, 'Засгийн газрын шийдвэр гарсан', null, true, false);
insert into data_landuse.cl_landsue_movement_status values (9, 'Баталгаажуулах', null, false, false);

--------------------
DROP TABLE if exists  data_landuse.st_workflow cascade;
CREATE TABLE data_landuse.st_workflow
(
  id serial NOT NULL,
  code character varying(30) NOT NULL,
  name character varying(256),
  description text,
  type character varying(25),
  system_id integer,
  CONSTRAINT st_workflow_pkey PRIMARY KEY (id),
  CONSTRAINT st_workflow_uk UNIQUE (code)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_workflow
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.st_workflow TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow TO land_office_administration;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow TO role_management;

insert into data_landuse.st_workflow values (1, '1', 'Атар газрыг тариаланд шилжүүлэх', 'Тариалангийн тухай хууль- БХБЯ, ХХААЯ-тай хамтран');
insert into data_landuse.st_workflow values (2, '2', 'Атаршсан газрыг бэлчээрт шилжүүлэх', 'Тариалангийн тухай хууль- БХБЯ, ХХААЯ-тай хамтран');
insert into data_landuse.st_workflow values (3, '3', 'Хот, тосгон, бусад суурин газрын хилийн заагийг шинээр тогтоох', 'Газрын тухай хууль- БХБЯ, газрын асуудал эрхэлсэн төрийн захиргааны байгууллага');
insert into data_landuse.st_workflow values (4, '4', 'Автозам, төмөр зам болон шугам сүлжээ шинээр барьж байгуулах', 'Газрын тухай, бусад холбогдох хууль- БХБЯ, асуудал хариуцсан төрийн захиргааны төв байгууллагууд');
insert into data_landuse.st_workflow values (5, '5', 'Ашигт малтмалын орд газар шинээр байгуулах', 'Газрын тухай, ашигт малтмалын тухай хууль- БХБЯ, УУЯ');
insert into data_landuse.st_workflow values (6, '6', 'Ойн сан бүхий газрыг бусад үндсэн ангилалд шилжүүлэх', 'Газрын тухай хууль, Ойн тухай хууль- БХБЯ, БОАЖЯ');
insert into data_landuse.st_workflow values (7, '7', 'Бусад ангиллаас ойн сан бүхий газарт шилжүүлэх', 'Газрын тухай хууль, Ойн тухай хууль- БХБЯ, БОАЖЯ');
insert into data_landuse.st_workflow values (8, '8', 'Усны сан бүхий газрыг бусад үндсэн ангилалд шилжүүлэх', 'Газрын тухай хууль, усны тухай хууль- БХБЯ, БОАЖЯ');
insert into data_landuse.st_workflow values (9, '9', 'Бусад ангиллаас усны сан бүхий газарт шилжүүлэх', 'Газрын тухай хууль, усны тухай хууль- БХБЯ, БОАЖЯ');

-----------------------
DROP TABLE if exists  data_landuse.st_workflow_status cascade;
CREATE TABLE data_landuse.st_workflow_status
(
  workflow_id integer references data_landuse.st_workflow on update cascade on delete restrict,
  prev_status_id integer references data_landuse.cl_landsue_movement_status on update cascade on delete restrict,
  next_status_id integer references data_landuse.cl_landsue_movement_status on update cascade on delete restrict,
  id serial NOT NULL,
  CONSTRAINT st_workflow_status_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_workflow_status
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.st_workflow_status TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow_status TO land_office_administration;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow_status TO role_management;

-----------------------
DROP TABLE if exists  data_landuse.st_workflow_status_landuse cascade;
CREATE TABLE data_landuse.st_workflow_status_landuse
(
  workflow_id integer references data_landuse.st_workflow on update cascade on delete restrict,
  prev_landuse integer references codelists.cl_landuse_type on update cascade on delete restrict,
  next_landuse integer references codelists.cl_landuse_type on update cascade on delete restrict,
  id serial NOT NULL,
  CONSTRAINT st_workflow_status_landuse_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_workflow_status_landuse
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.st_workflow_status_landuse TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow_status_landuse TO land_office_administration;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_workflow_status_landuse TO role_management;

--

DROP TABLE if exists  data_landuse.ca_landuse_static cascade;
CREATE TABLE data_landuse.ca_landuse_static
(
  id serial NOT NULL PRIMARY KEY,
  landuse integer references codelists.cl_landuse_type on update cascade on delete restrict,
  current_year integer,
  area_ga numeric,
  parcel_count integer,
  level_type integer
  
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.ca_landuse_static
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.ca_landuse_static TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_static TO land_office_administration, cadastre_update, contracting_update, application_update;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.ca_landuse_static TO role_management;

