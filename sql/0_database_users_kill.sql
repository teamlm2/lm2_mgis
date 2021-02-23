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

Select * from pg_stat_activity where state='idle';

SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE pid = 67757

SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE datname = 'lm_0003'
AND pid <> pg_backend_pid()
AND state in ('idle');

SELECT * FROM pg_stat_activity WHERE datname = 'lm_0003' and state = 'active';

SELECT
  pid,
  application_name,
  now() - pg_stat_activity.query_start AS duration,
  query,
  state
FROM pg_stat_activity
WHERE datname = 'lm_0003' 
and state = 'active' 
and (now() - pg_stat_activity.query_start) > interval '5 minutes'
order by now() - pg_stat_activity.query_start;