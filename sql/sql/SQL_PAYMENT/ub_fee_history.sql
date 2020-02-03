CREATE TABLE data_ub.ub_fee_history
(
  id serial NOT NULL primary key,
  no character varying(255),
  person_register character varying(255),
  pid character varying(255),
  contract_no character varying(255),
  document_area numeric,
  zoriulalt character varying(500),
  ner character varying(500),
  payment_contract numeric,
  payment_before_less numeric,
  payment_before_over numeric,
  payment_year numeric,
  payment_fund numeric,
  payment_loss numeric,
  payment_total numeric,
  paid_before_less numeric,
  paid_year numeric,
  paid_fund numeric,
  paid_city numeric,
  paid_district numeric,
  invalid_payment numeric,
  paid_less numeric,
  paid_over numeric,
  description character varying(500),
  decision character varying(500),
  current_year integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_ub.ub_fee_history
  OWNER TO geodb_admin;

GRANT ALL ON TABLE data_ub.ub_fee_history TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_ub.ub_fee_history TO contracting_update;
GRANT SELECT ON TABLE data_ub.ub_fee_history TO contracting_view;
GRANT SELECT ON TABLE data_ub.ub_fee_history TO reporting;

-----
GRANT ALL ON SEQUENCE data_ub.ub_fee_history_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_ub.ub_fee_history_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_ub.ub_fee_history_id_seq TO application_update;