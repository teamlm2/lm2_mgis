ALTER TABLE data_address.ca_parcel_address ADD COLUMN status int references data_address.cl_address_status on update cascade on delete restrict;

ALTER TABLE data_address.ca_parcel_address ADD COLUMN parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict;

ALTER TABLE data_address.ca_parcel_address ADD COLUMN geometry geometry(Polygon,4326);

ALTER TABLE data_address.ca_building_address ADD COLUMN status int references data_address.cl_address_status on update cascade on delete restrict;

ALTER TABLE data_address.ca_building_address ADD COLUMN parcel_type int references codelists.cl_parcel_type on update cascade on delete restrict;

ALTER TABLE data_address.ca_building_address ADD COLUMN geometry geometry(Polygon,4326);

ALTER TABLE data_address.ca_parcel_address ADD COLUMN valid_from date DEFAULT ('now'::text)::date;
ALTER TABLE data_address.ca_parcel_address ADD COLUMN valid_till date DEFAULT 'infinity'::date;
ALTER TABLE data_address.ca_building_address ADD COLUMN valid_from date DEFAULT ('now'::text)::date;
ALTER TABLE data_address.ca_building_address ADD COLUMN valid_till date DEFAULT 'infinity'::date;

alter table codelists.cl_parcel_type ADD COLUMN layer_type int;

update codelists.cl_parcel_type set layer_type = 1;

insert into codelists.cl_parcel_type (code, description, table_name, python_model_name, layer_type) values (7, 'Байр зүйн зургийн давхарга нэгж талбар', '', '', 1);
insert into codelists.cl_parcel_type (code, description, table_name, python_model_name, layer_type) values (8, 'Кадастрын үндсэн давхарга барилга', 'data_soums_union.ca_building_tbl', 'CaBuildingTbl', 2);
insert into codelists.cl_parcel_type (code, description, table_name, python_model_name, layer_type) values (9, 'Кадастрын ажлын давхарга барилга', 'data_soums_union.ca_tmp_building', 'CaTmpBuilding', 2);
insert into codelists.cl_parcel_type (code, description, table_name, python_model_name, layer_type) values (10, 'Байр зүйн зургийн давхарга барилга', '', '', 2);

update codelists.cl_parcel_type set layer_type = 2 where layer_type is null;