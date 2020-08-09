insert into codelists.cl_ub_edit_status (code, description, description_en) values(40, 'Устгагдсан', '4');

alter TABLE data_ub.ca_ub_parcel_tbl add COLUMN deleted_status_date date DEFAULT now();
alter TABLE data_ub.ca_ub_parcel_tbl add COLUMN deleted_status_decision_date date;
alter TABLE data_ub.ca_ub_parcel_tbl add COLUMN deleted_status_decision_no text;
alter TABLE data_ub.ca_ub_parcel_tbl add COLUMN deleted_status_comment text;
alter TABLE data_ub.ca_ub_parcel_tbl add COLUMN deleted_status_user text;