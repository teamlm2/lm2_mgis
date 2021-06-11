--NEGJ TALBAR
select cpt.parcel_id, cpt.old_parcel_id, cpt.landuse, clt.description landuse_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, cpt.property_no, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry, cpt.updated_at
from data_soums_union.ca_parcel_tbl cpt 
join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpt.au3 = au3.code
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between '1900-01-01'::date and cpt.valid_till limit 1

--BARILGA
select cpt.building_id , cpt.building_no , cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry,  cpt.updated_at
from data_soums_union.ca_building_tbl cpt 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between '1900-01-01'::date and cpt.valid_till limit 1

--HAYAG
select cpt.parcel_id, cpt.old_parcel_id, cpt.landuse, clt.description landuse_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, aza.code as postzone_code,
ss.code as street_code,
case 
	when cpa.gn_geo_id is null then ss.code
	else gs.geo_id 
end as address_streetcode, 
case 
	when cpa.gn_geo_id is null then ss."name"
	else gs."text" 
end as address_streetname, 
cpa.address_parcel_no, cpt.geometry, cpa.updated_at
from data_soums_union.ca_parcel_tbl cpt 
join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpt.au3 = au3.code
left join data_address.ca_parcel_address cpa on cpt.parcel_id = cpa.parcel_id 
left join data_address.st_street ss on cpa.street_id = ss.id 
left join data_address_import.gn_soft gs on cpa.gn_geo_id = gs.geo_id 
left join data_address.au_zipcode_area aza on st_within(st_centroid(cpa.geometry), aza.geometry)
where cpa.is_active is true and now() between '1900-01-01'::date and cpt.valid_till 
and cpt.geo_id is not null
limit 100

--LANDUSE
select cltt.parcel_id, cltt.cad_parcel_id, cltt.area_m2, cltt.valid_from, cltt.valid_till,
clt1.code lcode1, clt1.description as lcode1_desc,
clt2.code lcode2, clt2.description as lcode2_desc,
cltt.landuse lcode3, clt.description as lcode3_desc,
au1.code au1_code, au1.name as au1_name, cltt.au2 as au2_code, au2.name as au2_name, cltt.au3 as au3_code, au3."name" as au3_name,
clt.fill_color, clt.boundary_color, clt.boundary_width, 
cltt.geometry, cltt.updated_at 
from data_landuse.ca_landuse_type_tbl cltt 
left join codelists.cl_landuse_type clt on cltt.landuse = clt.code 
left join codelists.cl_landuse_type clt1 on clt.code1 = clt1.code 
left join codelists.cl_landuse_type clt2 on clt.code2 = clt2.code 
left join admin_units.au_level2 au2 on cltt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cltt.au3 = au3.code
where is_active is true and now() between '1900-01-01'::date and cltt.valid_till
limit 10

--MATERLIZED VIEW 
--NEGJ TALBAR
CREATE MATERIALIZED VIEW data_address_import.mgis_cad_parcel AS 
select cpt.parcel_id, cpt.old_parcel_id, cpt.landuse, clt.description landuse_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, cpt.property_no, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry, cpt.updated_at
from data_soums_union.ca_parcel_tbl cpt 
join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpt.au3 = au3.code
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between '1900-01-01'::date and cpt.valid_till
WITH DATA;
ALTER TABLE data_address_import.mgis_cad_parcel
  OWNER TO geodb_admin;

--BARILGA
DROP MATERIALIZED VIEW data_address_import.mgis_building_parcel cascade;
CREATE MATERIALIZED VIEW data_address_import.mgis_building_parcel AS 
select cpt.building_id , cpt.building_no , cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry, updated_at
from data_soums_union.ca_building_tbl cpt 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between '1900-01-01'::date and cpt.valid_till
WITH DATA;
ALTER TABLE data_address_import.mgis_building_parcel
  OWNER TO geodb_admin;

--HAYAG
DROP MATERIALIZED VIEW data_address_import.mgis_address_parcel cascade;
CREATE MATERIALIZED VIEW data_address_import.mgis_address_parcel AS 
select cpt.parcel_id, cpt.old_parcel_id, cpt.landuse, clt.description landuse_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, aza.code as postzone_code,
ss.code as street_code,
case 
	when cpa.gn_geo_id is null then ss.code
	else gs.geo_id 
end as address_streetcode, 
case 
	when cpa.gn_geo_id is null then ss."name"
	else gs."text" 
end as address_streetname, 
cpa.address_parcel_no, cpt.geometry, cpt.updated_at
from data_soums_union.ca_parcel_tbl cpt 
join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpt.au3 = au3.code
left join data_address.ca_parcel_address cpa on cpt.parcel_id = cpa.parcel_id 
left join data_address.st_street ss on cpa.street_id = ss.id 
left join data_address_import.gn_soft gs on cpa.gn_geo_id = gs.geo_id 
left join data_address.au_zipcode_area aza on st_within(st_centroid(cpa.geometry), aza.geometry)
where cpa.is_active is true and now() between '1900-01-01'::date and cpt.valid_till 
and cpt.geo_id is not null
WITH DATA;
ALTER TABLE data_address_import.mgis_address_parcel
  OWNER TO geodb_admin;

--LANDUSE
DROP MATERIALIZED VIEW data_address_import.mgis_landuse_parcel cascade;
CREATE MATERIALIZED VIEW data_address_import.mgis_landuse_parcel AS 
select cltt.parcel_id, cltt.cad_parcel_id, cltt.area_m2, cltt.valid_from, cltt.valid_till,
clt1.code lcode1, clt1.description as lcode1_desc,
clt2.code lcode2, clt2.description as lcode2_desc,
cltt.landuse lcode3, clt.description as lcode3_desc,
au1.code au1_code, au1.name as au1_name, cltt.au2 as au2_code, au2.name as au2_name, cltt.au3 as au3_code, au3."name" as au3_name,
clt.fill_color, clt.boundary_color, clt.boundary_width, 
cltt.geometry, cltt.updated_at
from data_landuse.ca_landuse_type_tbl cltt 
left join codelists.cl_landuse_type clt on cltt.landuse = clt.code 
left join codelists.cl_landuse_type clt1 on clt.code1 = clt1.code 
left join codelists.cl_landuse_type clt2 on clt.code2 = clt2.code 
left join admin_units.au_level2 au2 on cltt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cltt.au3 = au3.code
where is_active is true and now() between '1900-01-01'::date and cltt.valid_till
WITH DATA;
ALTER TABLE data_address_import.mgis_landuse_parcel
  OWNER TO geodb_admin;

--15.27 deer unshuulah

--MATERLIZED VIEW 
--NEGJ TALBAR
--DROP MATERIALIZED VIEW public.view_mgis_cad_parcel;
CREATE MATERIALIZED VIEW public.view_mgis_cad_parcel AS 
SELECT * FROM 
dblink('hostaddr=192.168.15.204 port=5432 dbname=lm_0003 user=geodb_admin password=456mgis456', 
'select cpt.parcel_id, cpt.old_parcel_id, cpt.landuse, clt.description landuse_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, cpt.property_no, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry, cpt.updated_at
from data_soums_union.ca_parcel_tbl cpt 
join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpt.au3 = au3.code
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between ''1900-01-01''::date and cpt.valid_till') AS 
t(parcel_id text, old_parcel_id text, landuse int, landuse_desc text, area_m2 numeric, valid_from date, valid_till date, au1_code text, au1_name text, au2_code text,
au2_name text, au3_code text, au3_name text,property_no text,org_type int, org_type_desc text, geometry geometry, updated_at date)
WITH DATA;
ALTER TABLE public.view_mgis_cad_parcel
  OWNER TO lm_import_user;

--BARILGA
--DROP MATERIALIZED VIEW public.view_mgis_cad_building;
CREATE MATERIALIZED VIEW public.view_mgis_cad_building AS 
SELECT * FROM 
dblink('hostaddr=192.168.15.204 port=5432 dbname=lm_0003 user=geodb_admin password=456mgis456', 
'select cpt.building_id , cpt.building_no , cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.org_type, so.land_office_name as org_type_desc, cpt.geometry,  cpt.updated_at
from data_soums_union.ca_building_tbl cpt 
left join admin_units.au_level2 au2 on cpt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join sdplatform.sd_organization so on cpt.org_type = so.id 
where now() between ''1900-01-01''::date and cpt.valid_till') AS 
t(building_id text, building_no text, area_m2 numeric, valid_from date, valid_till date, au1_code text, au1_name text, au2_code text,
au2_name text, org_type int, org_type_desc text, geometry geometry, updated_at date)
WITH DATA;
ALTER TABLE public.view_mgis_cad_building
  OWNER TO lm_import_user;
  
--LANDUSE
--DROP MATERIALIZED VIEW public.view_mgis_landuse_parcel;
CREATE MATERIALIZED VIEW public.view_mgis_landuse_parcel AS 
SELECT * FROM 
dblink('hostaddr=192.168.15.204 port=5432 dbname=lm_0003 user=geodb_admin password=456mgis456', 
'select cltt.parcel_id, cltt.cad_parcel_id, cltt.area_m2, cltt.valid_from, cltt.valid_till,
clt1.code lcode1, clt1.description as lcode1_desc,
clt2.code lcode2, clt2.description as lcode2_desc,
cltt.landuse lcode3, clt.description as lcode3_desc,
au1.code au1_code, au1.name as au1_name, cltt.au2 as au2_code, au2.name as au2_name, cltt.au3 as au3_code, au3."name" as au3_name,
clt.fill_color, clt.boundary_color, clt.boundary_width, 
cltt.geometry, cltt.updated_at
from data_landuse.ca_landuse_type_tbl cltt 
left join codelists.cl_landuse_type clt on cltt.landuse = clt.code 
left join codelists.cl_landuse_type clt1 on clt.code1 = clt1.code 
left join codelists.cl_landuse_type clt2 on clt.code2 = clt2.code 
left join admin_units.au_level2 au2 on cltt.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cltt.au3 = au3.code
where is_active is true and now() between ''1900-01-01''::date and cltt.valid_till') AS 
t(parcel_id text, cad_parcel_id text, area_m2 numeric, valid_from date, valid_till date, lcode1 int, lcode1_desc text, lcode2 int, lcode2_desc text, lcode3 int, lcode3_desc text, au1_code text, au1_name text, au2_code text,
au2_name text, au3_code text, au3_name text, fill_color text, boundary_color text, boundary_width numeric, geometry geometry, updated_at date)
WITH DATA;
ALTER TABLE public.view_mgis_landuse_parcel
  OWNER TO lm_import_user;
  
--
--LANDUSE
--DROP MATERIALIZED VIEW public.view_mgis_address_parcel;
CREATE MATERIALIZED VIEW public.view_mgis_address_parcel AS 
SELECT * FROM 
dblink('hostaddr=192.168.15.204 port=5432 dbname=lm_0003 user=geodb_admin password=456mgis456', 
'select cpa.id, cpt.parcel_id cad_parcel_id, cpt.landuse, clt.description landuse_desc, cpa.parcel_type, cpt2.description as parcel_type_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, aza.code as postzone_code,
case 
	when cpa.gn_geo_id is null then ss.code
	else gs.geo_id 
end as address_streetcode, 
case 
	when cpa.gn_geo_id is null then ss."name"
	else gs."text" 
end as address_streetname, 
cpa.address_parcel_no, cpt.geometry, cpa.updated_at
from data_address.ca_parcel_address cpa 
join codelists.cl_landuse_type clt on cpa.landuse = clt.code 
left join codelists.cl_parcel_type cpt2 on cpa.parcel_type = cpt2.code 
left join admin_units.au_level2 au2 on cpa.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpa.au3 = au3.code
left join data_soums_union.ca_parcel_tbl cpt on cpa.parcel_id = cpt.parcel_id 
left join data_address.st_street ss on cpa.street_id = ss.id 
left join data_address_import.gn_soft gs on cpa.gn_geo_id = gs.geo_id 
left join data_address.au_zipcode_area aza on st_within(st_centroid(cpa.geometry), aza.geometry)
where cpa.is_active is true and now() between ''1900-01-01''::date and cpt.valid_till 
and cpt.geo_id is not null') AS 
t(id bigint, cad_parcel_id text, landuse int, landuse_desc text, parcel_type int, parcel_type_desc text, area_m2 numeric, valid_from date, valid_till date, au1_code text, au1_name text, au2_code text,
au2_name text, au3_code text, au3_name text, postzone_code text, address_streetcode text, address_streetname text, address_parcel_no text, geometry geometry, updated_at date)
WITH DATA;
ALTER TABLE public.view_mgis_address_parcel
  OWNER TO lm_import_user;

--LANDUSE
--DROP MATERIALIZED VIEW public.view_mgis_address_parcel;
CREATE MATERIALIZED VIEW public.view_mgis_address_parcel AS 
SELECT * FROM 
dblink('hostaddr=192.168.15.204 port=5432 dbname=lm_0003 user=geodb_admin password=456mgis456', 
'select cpa.id, cpt.parcel_id cad_parcel_id, cpt.landuse, clt.description landuse_desc, cpa.parcel_type, cpt2.description as parcel_type_desc, cpt.area_m2, cpt.valid_from, cpt.valid_till, 
au1.code au1_code, au1.name as au1_name, cpt.au2 as au2_code, au2.name as au2_name, cpt.au3 as au3_code, au3."name" as au3_name, aza.code as postzone_code,
case 
	when cpa.gn_geo_id is null then ss.code
	else gs.geo_id 
end as address_streetcode, 
case 
	when cpa.gn_geo_id is null then ss."name"
	else gs."text" 
end as address_streetname, 
cpa.address_parcel_no, cpt.geometry, cpa.updated_at
from data_address.ca_parcel_address cpa 
join codelists.cl_landuse_type clt on cpa.landuse = clt.code 
left join codelists.cl_parcel_type cpt2 on cpa.parcel_type = cpt2.code 
left join admin_units.au_level2 au2 on cpa.au2 = au2.code 
left join admin_units.au_level1 au1 on au2.au1_code = au1.code 
left join admin_units.au_level3 au3 on cpa.au3 = au3.code
left join data_soums_union.ca_parcel_tbl cpt on cpa.parcel_id = cpt.parcel_id 
left join data_address.st_street ss on cpa.street_id = ss.id 
left join data_address_import.gn_soft gs on cpa.gn_geo_id = gs.geo_id 
left join data_address.au_zipcode_area aza on st_within(st_centroid(cpa.geometry), aza.geometry)
where cpa.is_active is true and now() between ''1900-01-01''::date and cpt.valid_till 
and cpt.geo_id is not null') AS 
t(id bigint, cad_parcel_id text, landuse int, landuse_desc text, parcel_type int, parcel_type_desc text, area_m2 numeric, valid_from date, valid_till date, au1_code text, au1_name text, au2_code text,
au2_name text, au3_code text, au3_name text, postzone_code text, address_streetcode text, address_streetname text, address_parcel_no text, geometry geometry, updated_at date)
WITH DATA;
ALTER TABLE public.view_mgis_address_parcel
  OWNER TO lm_import_user;