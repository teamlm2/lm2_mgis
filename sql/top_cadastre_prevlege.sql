﻿do
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