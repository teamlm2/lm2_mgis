--CREATE ROLE reporting;
--CREATE ROLE address_update;
--CREATE ROLE geodb_admin;

DROP SCHEMA IF EXISTS data_sei CASCADE;
CREATE SCHEMA data_sei;
GRANT USAGE ON SCHEMA data_sei TO public;
SET SEARCH_PATH TO data_sei, admin_units, public;

-------------

CREATE TABLE data_sei.sei_cl_attribute_group
(
  attribute_group_id serial PRIMARY KEY,
  code character varying(50) NOT NULL,
  group_name character varying(256) NOT NULL,
  is_active boolean NOT NULL,
  description text,
  created_at timestamp without time zone,
  created_by integer,
  updated_at timestamp without time zone,
  updated_by integer,
  parent_attribute_group_id integer
);
grant select, insert, update, delete on sei_cl_attribute_group to geodb_admin;
grant select on sei_cl_attribute_group to reporting;
COMMENT ON TABLE sei_cl_attribute_group
  IS 'Аттрибутын групп';

CREATE TABLE data_sei.sei_cl_attribute
(
  attribute_id serial PRIMARY KEY,
  attribute_name character varying(10) NOT NULL,
  attribute_name_mn character varying(256) NOT NULL,
  is_active boolean NOT NULL,
  attribute_data_type character varying(50) NOT NULL, -- Үзүүлэлтийн өгөгдлийн төрөл...
  description text,
  created_at timestamp without time zone,
  created_by integer,
  updated_at timestamp without time zone,
  updated_by integer,
  attribute_group_id int references sei_cl_attribute_group on update cascade on delete restrict,
  length integer,
  query_text character varying(250)
);
grant select, insert, update, delete on sei_cl_attribute to geodb_admin;
grant select on sei_cl_attribute to reporting;
COMMENT ON TABLE sei_cl_attribute
  IS 'Аттрибутын жагсаалт';

CREATE TABLE data_sei.sei_cl_attribute_lov_value
(
  attribute_lov_value_id serial PRIMARY KEY,
  attribute_id int references sei_cl_attribute on update cascade on delete restrict,
  code character varying(50) NOT NULL,
  name character varying(256) NOT NULL,
  is_active boolean NOT NULL,
  created_at timestamp without time zone,
  created_by integer,
  updated_at timestamp without time zone,
  updated_by integer
);
grant select, insert, update, delete on sei_cl_attribute_lov_value to geodb_admin;
grant select on sei_cl_attribute_lov_value to reporting;
COMMENT ON TABLE sei_cl_attribute_lov_value
  IS 'Үзүүлэлтийн сонголтод утга';

CREATE TABLE data_sei.sei_cl_attribute_value_result
(
  attribute_value_result_id serial PRIMARY KEY,
  attribute_id int references sei_cl_attribute on update cascade on delete restrict,
  min_value numeric, -- Хамгийн бага утга
  max_value numeric, -- Хамгийн их утга
  result character varying(50) NOT NULL, -- Үнэлгээ...
  created_at timestamp without time zone,
  created_by integer,
  updated_at timestamp without time zone,
  updated_by integer
);
grant select, insert, update, delete on sei_cl_attribute_value_result to geodb_admin;
grant select on sei_cl_attribute_value_result to reporting;
COMMENT ON TABLE sei_cl_attribute_value_result
  IS 'Үзүүлэлтийн утгаас хамаарсан үнэлгээ';




