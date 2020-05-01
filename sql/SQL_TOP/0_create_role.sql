do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'top_admin') THEN

      create role top_admin createdb createrole login password 'top_admin';
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'top_cadastre_view') THEN

      create role top_cadastre_view;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'top_cadastre_update') THEN

      create role top_cadastre_update;
   END IF;
END
$body$;



DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'utop010101') THEN

      CREATE ROLE utop010101 LOGIN PASSWORD 'utop010101';
   END IF;
END
$body$;

GRANT top_cadastre_update TO utop010101;
GRANT top_cadastre_view TO utop010101;

