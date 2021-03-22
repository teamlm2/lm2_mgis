select x1.*, x2.count, x3.count, x4.count from (
select au1.code, count(app.app_id), round(coalesce(sum(ex8.monetary_unit_value), 0)/1000000, 2) as sum from admin_units.au_level1 au1
left join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
left join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
where app.app_type = 8 and DATE_PART('year', ex8.start_mortgage_period) <= 2020
group by au1.code
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x1
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
left join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
left join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
where app.app_type = 8 and ex8.mortgage_status = 10 and DATE_PART('year', ex8.start_mortgage_period) <= 2020
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x2 on x1.code = x2.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
left join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
left join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
where app.app_type = 8 and ex8.mortgage_status = 20 and DATE_PART('year', ex8.start_mortgage_period) <= 2020
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x3 on x1.code = x3.code
left join (select au1.code, count(app.app_id)
 from admin_units.au_level1 au1
left join data_soums_union.ct_application app on substring(app.au2, 1, 3) = au1.code
left join data_soums_union.ct_app8_ext ex8 on app.app_id = ex8.app_id
where app.app_type = 8 and ex8.mortgage_status = 30 and DATE_PART('year', ex8.start_mortgage_period) <= 2020
group by au1.code, ex8.mortgage_status
order by round(coalesce(sum(ex8.monetary_unit_value), 0), 2) asc)x4 on x1.code = x4.code

--where  and x1.code = x3.code --and x1.code = x4.code