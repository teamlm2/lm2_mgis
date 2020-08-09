insert into data_cama.cm_parcel_factor_value(parcel_id, factor_id, factor_value, in_active, year_value)

select * from (
select parcel.parcel_id, f.id, base.calculate_distance_cama_parcel_value(f.landuse_type, parcel.parcel_id) as factor_value, true, 2019 from data_soums_union.ca_parcel_tbl parcel, data_cama.cm_factor f
where parcel.geometry is not null
and substring(parcel.au2, 1, 3) != '011' 
and f.landuse_type is not null
--and parcel.parcel_id = 'E654000003'
--order by f.id
--limit 10
)xxx where factor_value is not null
--limit 200
on conflict(parcel_id, year_value, factor_id, in_active) do nothing;


