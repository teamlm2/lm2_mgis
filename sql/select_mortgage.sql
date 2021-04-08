CREATE OR REPLACE VIEW data_soums_union.view_mortgage_report_consolidated AS 
select x1.*, coalesce(x2.count, 0) status_10, coalesce(x3.count, 0) status_20, coalesce(x4.count, 0) status_30, coalesce(x5.count, 0) right_type_2, coalesce(x6.count, 0) right_type_3,
coalesce(x7.count, 0) landuse_22, coalesce(x8.count, 0) landuse_21, coalesce(x9.count, 0) landuse_23, coalesce(x10.count, 0) landuse_1, coalesce(x11.count, 0) person_type_1, coalesce(x12.count, 0) person_type_2,
coalesce(x13.count, 0) person_mort_all, coalesce(x14.count, 0) person_mort_1, coalesce(x15.count, 0) person_mort_2, x16.max_price_sum, x16.min_price_sum, x16.avg_price_sum from (
select au1.code, count(app.app_id) all_count, sum(p.area_m2) all_area_m2, round(coalesce(sum(ex8.monetary_unit_value), 0)/1000000, 2) as price_sum from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x1
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and ex8.mortgage_status = 10 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x2 on x1.code = x2.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and ex8.mortgage_status = 20 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x3 on x1.code = x3.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and ex8.mortgage_status = 30 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x4 on x1.code = x4.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and app.right_type = 2 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code, app.right_type)x5 on x1.code = x5.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and app.right_type = 3 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code, app.right_type)x6 on x1.code = x6.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
where app.app_type = 8 and p.parcel_id is not null and cl.code2 = 22 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x7 on x1.code = x7.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
where app.app_type = 8 and p.parcel_id is not null and cl.code2 = 21 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x8 on x1.code = x8.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
where app.app_type = 8 and p.parcel_id is not null and cl.code2 = 23 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x9 on x1.code = x9.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
where app.app_type = 8 and p.parcel_id is not null and cl.code1 = 1 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x10 on x1.code = x10.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
inner join data_soums_union.ct_application_person_role pr on app.app_id = pr.application
inner join base.bs_person person on pr.person = person.person_id
where app.app_type = 8 and p.parcel_id is not null and pr.role = 10 and person.type in (10, 20, 50) and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x11 on x1.code = x11.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
inner join data_soums_union.ct_application_person_role pr on app.app_id = pr.application
inner join base.bs_person person on pr.person = person.person_id
where app.app_type = 8 and p.parcel_id is not null and pr.role = 10 and person.type not in (10, 20, 50) and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x12 on x1.code = x12.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
inner join data_soums_union.ct_application_person_role pr on app.app_id = pr.application
inner join base.bs_person person on pr.person = person.person_id
where app.app_type = 8 and p.parcel_id is not null and pr.role = 50 and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x13 on x1.code = x13.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
inner join data_soums_union.ct_application_person_role pr on app.app_id = pr.application
inner join base.bs_person person on pr.person = person.person_id
where app.app_type = 8 and p.parcel_id is not null and pr.role = 50 and person.type in (10, 20, 50) and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x14 on x1.code = x14.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
inner join codelists.cl_landuse_type cl on p.landuse = cl.code
inner join data_soums_union.ct_application_person_role pr on app.app_id = pr.application
inner join base.bs_person person on pr.person = person.person_id
where app.app_type = 8 and p.parcel_id is not null and pr.role = 50 and person.type not in (10, 20, 50) and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code)x15 on x1.code = x15.code
left join (select au1.code, round(coalesce(avg(ex8.monetary_unit_value), 0)/1000000, 2) as avg_price_sum, round(coalesce(max(ex8.monetary_unit_value), 0)/1000000, 2) as max_price_sum, round(coalesce(min(ex8.monetary_unit_value), 0)/1000000, 2) as min_price_sum from admin_units.au_level1 au1
join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
inner join data_soums_union.ca_parcel_tbl p on app.parcel = p.parcel_id
where app.app_type = 8 and p.parcel_id is not null and DATE_PART('year', ex8.start_mortgage_period) <= DATE_PART('year', now())
group by au1.code
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x16 on x1.code = x16.code;

ALTER TABLE data_soums_union.view_mortgage_report_consolidated
  OWNER TO geodb_admin;