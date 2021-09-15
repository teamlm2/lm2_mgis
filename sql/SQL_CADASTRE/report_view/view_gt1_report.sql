set search_path to s06201, codelists, base, settings, admin_units, public;
create or replace view view_gt1_report as 
SELECT parcel.parcel_id,
    au1.name AS admin_unit1,
    au2.name AS admin_unit2,   
    parcel.address_streetname,
    parcel.address_khashaa,    
    substring(landuse.code::text, 1, 1)::integer AS lcode1,
    case 
	when substring(landuse.code::text, 1, 1)::integer = 1 then 'Хөдөө аж ахуйн газар газар'
	when substring(landuse.code::text, 1, 1)::integer = 2 then 'Хот, тосгон, бусад суурины газар'
	when substring(landuse.code::text, 1, 1)::integer = 3 then 'Зам шугам сүлжээний газар'
	when substring(landuse.code::text, 1, 1)::integer = 4 then 'Ойн сан бүхий газар'
	when substring(landuse.code::text, 1, 1)::integer = 5 then 'Усны сан бүхий газар'
	when substring(landuse.code::text, 1, 1)::integer = 6 then 'Улсын тусгай хэрэгцээний газар'
	else 'Хоосон'
    end as lcode1_desc,
    landuse.code2 AS lcode2,
    landuse.description2 as lcode2_desc,
    landuse.code AS lcode3,
    landuse.description as lcode3_desc,
    parcel.area_m2 / 10000::numeric AS area_ha,
    parcel.area_m2,
    parcel.geometry
FROM s06201.ca_parcel_tbl parcel
JOIN codelists.cl_landuse_type landuse ON parcel.landuse = landuse.code
JOIN admin_units.au_cadastre_block block ON st_within(parcel.geometry, block.geometry)
join admin_units.au_level1 au1 on au1.code = substring(block.soum_code,1,3)
join admin_units.au_level2 au2 on au2.code = block.soum_code
where user in (select user_name from set_role) AND 
	overlaps(valid_from, valid_till, (SELECT pa_from from set_role where user_name = user), (select pa_till from set_role where user_name = user));

grant select, insert, update, delete on view_gt1_report to cadastre_update;
grant select on view_gt1_report to cadastre_view, reporting;