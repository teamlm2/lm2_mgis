alter table codelists.cl_application_type add column is_meeting boolean default false;

--------
DROP TABLE if exists data_soums_union.set_meeting_app_conf;
CREATE TABLE data_soums_union.set_meeting_app_conf
(
  id serial PRIMARY KEY,
  app_type int references codelists.cl_application_type on update cascade on delete restrict,
  department_id int references sdplatform.hr_department on update cascade on delete restrict,  
  decision_level int references codelists.cl_decision_level on update cascade on delete restrict,
  check_status_id int references codelists.cl_application_status on update cascade on delete restrict,
  approved_status_id int references codelists.cl_application_status on update cascade on delete restrict,
  decline_status_id int references codelists.cl_application_status on update cascade on delete restrict,  
  created_by integer,
  updated_by integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone NOT NULL DEFAULT now(),
  UNIQUE (app_type, department_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_soums_union.set_meeting_app_conf
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.set_meeting_app_conf TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.set_meeting_app_conf TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.set_meeting_app_conf TO application_update;
GRANT SELECT, INSERT ON TABLE data_soums_union.set_meeting_app_conf TO application_view;

------

DROP TABLE if exists codelists.cl_meeting_status cascade;
CREATE TABLE codelists.cl_meeting_status
(
  id serial PRIMARY KEY,
  code text NOT NULL UNIQUE,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75),
  color character varying(7)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_meeting_status
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_meeting_status TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_meeting_status TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_meeting_status TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_meeting_status TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_meeting_status TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_meeting_status TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_meeting_status TO reporting;
COMMENT ON TABLE codelists.cl_meeting_status
  IS 'Хурлын явц';
  
insert into codelists.cl_meeting_status(code, description) values ('1', 'Хурал заралсан');
insert into codelists.cl_meeting_status(code, description) values ('2', 'Хүлээгдэж байгаа');
insert into codelists.cl_meeting_status(code, description) values ('3', 'Шийдвэр гарсан');

DROP TABLE if exists codelists.cl_meeting_app_status cascade;
CREATE TABLE codelists.cl_meeting_app_status
(
  id serial PRIMARY KEY,
  code text NOT NULL UNIQUE,
  description character varying(75) NOT NULL UNIQUE,
  description_en character varying(75),
  color character varying(7)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE codelists.cl_meeting_app_status
  OWNER TO geodb_admin;
GRANT ALL ON TABLE codelists.cl_meeting_app_status TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE codelists.cl_meeting_app_status TO land_office_administration;
GRANT SELECT ON TABLE codelists.cl_meeting_app_status TO cadastre_view;
GRANT SELECT ON TABLE codelists.cl_meeting_app_status TO cadastre_update;
GRANT SELECT ON TABLE codelists.cl_meeting_app_status TO contracting_view;
GRANT SELECT ON TABLE codelists.cl_meeting_app_status TO contracting_update;
GRANT SELECT ON TABLE codelists.cl_meeting_app_status TO reporting;
COMMENT ON TABLE codelists.cl_meeting_app_status
  IS 'Хурлаас өргөдөлд өгөх явц';
  
insert into codelists.cl_meeting_app_status(code, description) values ('1', 'Зөвшөөрсөн');
insert into codelists.cl_meeting_app_status(code, description) values ('2', 'Зөвшөөрөөгүй');
  
DROP TABLE if exists data_soums_union.ct_meeting cascade;
CREATE TABLE data_soums_union.ct_meeting
(
  meeting_id serial PRIMARY KEY,
  meeting_no character varying(20) NOT NULL UNIQUE,
  meeting_date date not null,
  start_date date NOT NULL,
  end_date date NOT NULL,
  created_by integer,
  updated_by integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone NOT NULL DEFAULT now(),
  meeting_type integer,  
  decision_level int references codelists.cl_decision_level on update cascade on delete restrict,
  app_count integer,
  meeting_status_id int references codelists.cl_meeting_status on update cascade on delete restrict,
  department_id int references sdplatform.hr_department on update cascade on delete restrict,  
  au2 character varying(5) DEFAULT NULL::character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_soums_union.ct_meeting
  OWNER TO geodb_admin;
  
GRANT ALL ON TABLE data_soums_union.ct_meeting TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.ct_meeting TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.ct_meeting TO application_update;
GRANT SELECT, INSERT ON TABLE data_soums_union.ct_meeting TO application_view;
  
DROP TABLE if exists data_soums_union.ct_meeting_application cascade;
CREATE TABLE data_soums_union.ct_meeting_application
(
  application_id int references data_soums_union.ct_application on update cascade on delete restrict,
  meeting_id int references data_soums_union.ct_meeting on update cascade on delete restrict,
  meeting_app_status_id int references codelists.cl_meeting_app_status on update cascade on delete restrict,
  description text,
  created_by integer,
  updated_by integer,
  created_at timestamp without time zone NOT NULL DEFAULT now(),
  updated_at timestamp without time zone NOT NULL DEFAULT now(),
  CONSTRAINT ct_meeting_application_pkey PRIMARY KEY (application_id, meeting_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_soums_union.ct_meeting_application
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.ct_meeting_application TO geodb_admin;
GRANT SELECT ON TABLE data_soums_union.ct_meeting_application TO reporting;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.ct_meeting_application TO application_update;
GRANT SELECT, INSERT ON TABLE data_soums_union.ct_meeting_application TO application_view;

DROP TABLE if exists data_soums_union.ct_meeting_document cascade;
CREATE TABLE data_soums_union.ct_meeting_document
(
  meeting_id int references data_soums_union.ct_meeting on update cascade on delete restrict,
  document_id integer NOT NULL,
  role integer,
  CONSTRAINT ct_meeting_document_pkey PRIMARY KEY (meeting_id, document_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_soums_union.ct_meeting_document
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.ct_meeting_document TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.ct_meeting_document TO contracting_update;
GRANT SELECT ON TABLE data_soums_union.ct_meeting_document TO contracting_view;
GRANT SELECT ON TABLE data_soums_union.ct_meeting_document TO reporting;