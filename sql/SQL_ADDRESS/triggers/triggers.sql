CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_address.st_street
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

CREATE TRIGGER update_area
  BEFORE INSERT OR UPDATE
  ON data_address.st_street_sub
  FOR EACH ROW
  EXECUTE PROCEDURE base.update_area_or_length();

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_address.st_street
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_address.st_street
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();

CREATE TRIGGER set_default_au1
  BEFORE INSERT OR UPDATE
  ON data_address.st_street_sub
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au1();

CREATE TRIGGER set_default_au2
  BEFORE INSERT OR UPDATE
  ON data_address.st_street_sub
  FOR EACH ROW
  EXECUTE PROCEDURE base.set_default_au2();
