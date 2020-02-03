insert into data_cama.cm_parcel_factor_value_ub(parcel_id, factor_id, factor_value, in_active, year_value)

select * from (
select parcel.old_parcel_id, f.id, base.ub_calculate_distance_cama_parcel(f.landuse_type, parcel.old_parcel_id) as factor_value, true, 2019 from data_ub.ca_ub_parcel_tbl parcel, data_cama.cm_factor f
where substring(parcel.au2, 1, 3) = '011' 
and parcel.geometry is not null
and f.landuse_type is not null
--and parcel.old_parcel_id = '18635314632495'
--order by f.id
--limit 100
)xxx where factor_value is not null
--limit 20
on conflict(parcel_id, year_value, factor_id, in_active) do nothing;


