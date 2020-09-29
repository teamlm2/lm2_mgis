SELECT
relname AS "table_name",
pg_size_pretty(pg_table_size(C.oid)) AS "table_size"
FROM
pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname NOT IN ('pg_catalog', 'information_schema') AND nspname !~ '^pg_toast' AND relkind IN ('r')
ORDER BY pg_table_size(C.oid)
DESC LIMIT 1;

SELECT relname, n_dead_tup FROM pg_stat_user_tables
order by n_dead_tup desc;

SELECT * FROM pg_stat_activity WHERE datname = 'lm_0003' and state = 'active';

SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE state = 'active' and pid <> pg_backend_pid();

ALTER DATABASE lm_0003 CONNECTION LIMIT 0;

ALTER DATABASE lm_0003 CONNECTION LIMIT -1;

vacuum full data_soums_union.ct_application;
vacuum full data_soums_union.ct_application;

vacuum full data_landuse.ca_landuse_type_tbl;
vacuum full data_soums_union."ca_parcel_tbl";