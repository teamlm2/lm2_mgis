insert into data_cama.cm_parcel_factor_value_ub(parcel_id, factor_id, factor_value, in_active, year_value, closets_parcel_id)

select * from (
select parcel.old_parcel_id, 3, base.ub_calculate_dem_cama_parcel(2, parcel.old_parcel_id) as factor_value, true, 2019, null from data_ub.ca_ub_parcel_tbl parcel 
left join (select b.old_parcel_id from data_cama.cm_parcel_factor_value_ub a 
inner join data_ub.ca_ub_parcel_tbl b on a.parcel_id = b.old_parcel_id and a.year_value is not null and a.factor_id = 2 and a.in_active = TRUE) bb on parcel.old_parcel_id = bb.old_parcel_id 
where bb.old_parcel_id is null and parcel.geometry is not null 
)xxx where factor_value is not null

on conflict(parcel_id, year_value, factor_id, in_active) do nothing;