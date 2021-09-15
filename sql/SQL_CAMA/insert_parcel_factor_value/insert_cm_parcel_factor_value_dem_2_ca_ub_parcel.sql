--# factor_id = 2; elevation
insert into data_cama.cm_parcel_factor_value_ub(parcel_id, factor_id, factor_value, in_active, year_value, closets_parcel_id)

select * from (
select parcel.old_parcel_id, 2, base.ub_calculate_dem_cama_parcel(1, parcel.old_parcel_id) as factor_value, true, 2019, null from data_ub.ca_ub_parcel_tbl parcel 
left join (select b.old_parcel_id from data_cama.cm_parcel_factor_value_ub a 
left join data_ub.ca_ub_parcel_tbl b on a.parcel_id = b.old_parcel_id and a.year_value is not null and a.factor_id = 2 and a.in_active = TRUE) bb on parcel.old_parcel_id = bb.old_parcel_id 
where bb.old_parcel_id is null and parcel.geometry is not null 
--and bb.old_parcel_id = '18303298355144'
--limit 10
)xxx where factor_value is not null
--limit 10 

on conflict(parcel_id, year_value, factor_id, in_active) do nothing;

------------


select * from data_ub.ca_ub_parcel_tbl parcel
where old_parcel_id = '18303298355144'