pg_restore -U postgres -d lm_8246 --disable-triggers D:/pasture.dump

---dump

pg_dump -U geodb_admin -h 192.168.78.20 -Fc -n admin_units -n base -n codelists data_soums_union -n pasture lm_8246 > D:\work\PASTURE\project_3_otor\sql\pasture_schema_restore\pasture.dump


----neg husnegt dumpalj sergeeh
pg_dump -U geodb_admin --table=data_soums_union.ca_pug_boundary --data-only --column-inserts lm_065 > D:\ca_pug_boundary.sql
pg_dump -U geodb_admin --table=data_soums_union.ca_pasture_parcel_tbl --data-only --column-inserts lm_065 > D:\ca_pasture_parcel_tbl.sql

alter table data_soums_union.ca_pug_boundary disable trigger a_create_pug_id;
alter table data_soums_union.ca_pasture_parcel_tbl disable trigger a_create_parcel_id;

psql -U postgres -h 66.181.168.74 lm_0002 < D:/ca_pug_boundary.sql
psql -U postgres -h 66.181.168.74 lm_0002 < D:/ca_pasture_parcel_tbl.sql

alter table data_soums_union.ca_pug_boundary enable trigger a_create_pug_id;
alter table data_soums_union.ca_pasture_parcel_tbl enable trigger a_create_parcel_id;


-----------schemiig sql --eer dumpalj sergeeh
pg_dump -U postgres --schema=base --data-only --column-inserts lm_065 > D:\base_11.sql
pg_dump -U postgres --schema=settings --data-only --column-inserts lm_065 > D:\settings_11.sql
pg_dump -U postgres --schema=data_soums_union --data-only --column-inserts lm_065 > D:\data_soums_union_11.sql

pg_dump -U postgres --schema=base --data-only --column-inserts lm_065 > D:\base_065.sql
pg_dump -U postgres --schema=data_soums_union --data-only --column-inserts lm_065 > D:\data_soums_union_065.sql

psql -U postgres lm_4401 < D:\work\PASTURE\aimags_data\aimags_pasture_schema_dumps\dornogovi\lm_4404_pasture.sql

psql -U geodb_admin lm_0002 < D:\settings.sql

pg_dump -U postgres -Fc -n data_soums_union -n settings -n sdplatform lm_065 > D:\data_soums_union_settings.dump
pg_dump -U postgres -Fc -n admin_units -n base -n data_soums_union -n settings lm_0002 > D:\data_soums_union_20181026.dump