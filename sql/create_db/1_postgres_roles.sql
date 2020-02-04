-- To be run by a user with 'createrole' privilege
-- creates all required group roles and two user roles (role_manager and role_reporting)
do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'geodb_admin') THEN

      create role geodb_admin createdb createrole login password 'geodb_admin';
   END IF;
END
$body$;
--drop role if exists compiler;
DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'compiler') THEN

      CREATE ROLE compiler LOGIN PASSWORD 'compiler';
   END IF;
END
$body$;

DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'bucardo') THEN

      CREATE ROLE bucardo LOGIN PASSWORD 'bucardo';
   END IF;
END
$body$;
--drop role if exists geodb_admin;

DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_catalog.pg_user
      WHERE  usename = 'geodb_admin') THEN

      create role geodb_admin createdb createrole login password 'geodb_admin';
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'land_office_administration') THEN

      create role land_office_administration;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'application_update') THEN

      create role application_update;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'application_view') THEN

      create role application_view;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'ub_parcel') THEN

      create role ub_parcel;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'db_creation') THEN

      create role db_creation createdb;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'role_management') THEN

      create role role_management createrole;
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

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'contracting_view') THEN

      create role contracting_view;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'contracting_update') THEN

      create role contracting_update;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'reporting') THEN

      create role reporting;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'log_view') THEN

      create role log_view;
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'role_manager') THEN

      create role role_manager login password 'role_manager';
   END IF;
END
$body$;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 'role_reporting') THEN

      create role role_reporting login password 'role_reporting';
   END IF;
END
$body$;

grant role_management to role_manager;
grant reporting to role_reporting;

--CREATE ROLE compiler LOGIN PASSWORD 'compiler';
GRANT cadastre_update TO compiler;
GRANT cadastre_view TO compiler;
GRANT application_update TO compiler;
GRANT application_view TO compiler;
GRANT contracting_update TO compiler;
GRANT contracting_view TO compiler;
GRANT db_creation TO compiler;
GRANT land_office_administration TO compiler;
GRANT reporting TO compiler;
GRANT role_management TO compiler;
GRANT contracting_update TO role_manager;

do
$body$
BEGIN
   IF NOT EXISTS (
      SELECT *
      FROM   pg_roles 
      WHERE  rolname = 's00000') THEN

      create role s00000;
   END IF;
END
$body$;

