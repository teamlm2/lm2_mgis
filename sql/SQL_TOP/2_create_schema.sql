CREATE SCHEMA data_top
  AUTHORIZATION top_admin;

GRANT ALL ON SCHEMA admin_units TO top_admin;
GRANT ALL ON SCHEMA base TO top_admin;
GRANT ALL ON SCHEMA codelists TO top_admin;
GRANT ALL ON SCHEMA sdplatform TO top_admin;
GRANT ALL ON SCHEMA settings TO top_admin;
GRANT ALL ON SCHEMA data_top TO top_admin;
grant usage on schema data_top to public;

GRANT ALL ON TABLE admin_units.au_level1 TO top_admin;
GRANT ALL ON TABLE admin_units.au_level2 TO top_admin;
GRANT ALL ON TABLE admin_units.au_level3 TO top_admin;

ALTER FUNCTION base.update_area_or_length()
  OWNER TO top_admin;