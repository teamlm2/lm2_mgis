set search_path to data_soums_union, base, public;

DROP TRIGGER parcel_log ON data_soums_union.ca_parcel_tbl;
DROP TRIGGER building_log ON data_soums_union.ca_building_tbl;
DROP TRIGGER person_log ON base.bs_person;

DROP TRIGGER fee_log ON data_soums_union.ct_fee;
DROP TRIGGER tax_and_price_log ON data_soums_union.ct_tax_and_price;


CREATE TRIGGER person_log
  AFTER INSERT OR UPDATE OR DELETE
  ON bs_person
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

CREATE TRIGGER parcel_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ca_parcel_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

  CREATE TRIGGER building_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ca_building_tbl
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

CREATE TRIGGER application_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ct_application
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

CREATE TRIGGER contract_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ct_contract
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

CREATE TRIGGER ownership_record_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ct_ownership_record
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();

CREATE TRIGGER decision_log
  AFTER INSERT OR UPDATE OR DELETE
  ON ct_decision
  FOR EACH ROW
  EXECUTE PROCEDURE log_changes();


