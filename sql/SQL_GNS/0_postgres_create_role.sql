do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'gns_admin') THEN

      create role gns_admin createdb createrole login password 'gns_admin';
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'cadastre_view') THEN

      create role cadastre_view;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'cadastre_update') THEN

      create role cadastre_update;
   END IF;
END
$body$;



DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'ugns010101') THEN

      CREATE ROLE ugns010101 LOGIN PASSWORD 'ugns010101';
   END IF;
END
$body$;

GRANT cadastre_update TO ugns010101;
GRANT cadastre_view TO ugns010101;

