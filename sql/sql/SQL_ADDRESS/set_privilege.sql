--CREATE ROLE cadastre_view;
--CREATE ROLE cadastre_view;
--CREATE ROLE cadastre_update;

SET SEARCH_PATH TO data_address, public;

GRANT USAGE ON SEQUENCE au_zipcode_area_id_seq TO cadastre_view, cadastre_update;
GRANT USAGE ON SEQUENCE ca_building_address_id_seq TO cadastre_view, cadastre_update;
GRANT USAGE ON SEQUENCE ca_parcel_address_id_seq TO cadastre_view, cadastre_update;
GRANT USAGE ON SEQUENCE st_road_id_seq TO cadastre_view, cadastre_update;
GRANT USAGE ON SEQUENCE st_street_id_seq TO cadastre_view, cadastre_update;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.au_zipcode_area TO cadastre_update;
GRANT SELECT ON TABLE data_address.au_zipcode_area TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.ca_building_address TO cadastre_update;
GRANT SELECT ON TABLE data_address.ca_building_address TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.ca_parcel_address TO cadastre_update;
GRANT SELECT ON TABLE data_address.ca_parcel_address TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.cl_address_source TO cadastre_update;
GRANT SELECT ON TABLE data_address.cl_address_source TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.cl_road_type TO cadastre_update;
GRANT SELECT ON TABLE data_address.cl_road_type TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.cl_street_type TO cadastre_update;
GRANT SELECT ON TABLE data_address.cl_street_type TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_road TO cadastre_update;
GRANT SELECT ON TABLE data_address.st_road TO cadastre_view;

GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_street TO cadastre_update;
GRANT SELECT ON TABLE data_address.st_street TO cadastre_view;

