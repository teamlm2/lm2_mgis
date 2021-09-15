create role external_view login password 'external_view';
create role external_update login password 'external_update';

GRANT SELECT ON TABLE data_address.st_road TO external_view;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_address.st_road TO external_update;