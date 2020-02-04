-- To be run by a user with 'createdb' privilege
drop database lm_0003;

create database lm_0003 template=template_postgis;

grant create on database lm_0003 to geodb_admin;