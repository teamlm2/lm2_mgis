ALTER TABLE data_address.ca_parcel_address ADD COLUMN status int references data_address.cl_address_status on update cascade on delete restrict;

ALTER TABLE data_address.ca_parcel_address ADD COLUMN parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict;

ALTER TABLE data_address.ca_parcel_address ADD COLUMN geometry geometry(Polygon,4326);