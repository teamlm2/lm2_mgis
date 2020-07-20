select p.parcel_id, l.parcel_id l_id from data_soums_union.ca_parcel_tbl p, data_landuse.ca_landuse_type_tbl l
where st_within(st_centroid(l.geometry), p.geometry)
limit 10

alter table data_landuse.ca_landuse_type_tbl add column cad_parcel_id varchar(10) references data_soums_union.ca_parcel_tbl on update cascade on delete restrict;

with new_numbers as (
select p.parcel_id, l.parcel_id l_id from data_soums_union.ca_parcel_tbl p, data_landuse.ca_landuse_type_tbl l
where st_within(st_centroid(l.geometry), p.geometry)
limit 10
)
update data_landuse.ca_landuse_type_tbl
  set cad_parcel_id = s.parcel_id
from new_numbers s
where data_landuse.ca_landuse_type_tbl.parcel_id = s.l_id;

alter table data_soums_union.ca_state_parcel_tbl set schema data_landuse;
alter table data_landuse.ca_state_parcel_tbl add column landuse_parcel_id int references data_landuse.ca_landuse_type_tbl on update cascade on delete restrict;
alter table data_landuse.ca_state_parcel_tbl add column is_active boolean NOT NULL DEFAULT true;
--alter table data_landuse.ca_state_parcel_tbl add column app_id int references data_landuse.ca_landuse_type_tbl on update cascade on delete restrict;