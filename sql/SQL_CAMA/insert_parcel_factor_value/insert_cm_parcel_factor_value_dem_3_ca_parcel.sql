--# factor_id = 2; elevation
insert into data_cama.cm_parcel_factor_value(parcel_id, factor_id, factor_value, in_active, year_value, closets_parcel_id)
select * from (
select parcel.parcel_id, 3, base.calculate_dem_cama_parcel(2, parcel.parcel_id) as factor_value, true, 2019, null from data_soums_union.ca_parcel_tbl parcel 
left join (select b.parcel_id from data_cama.cm_parcel_factor_value a 
inner join data_soums_union.ca_parcel_tbl b on a.parcel_id = b.parcel_id and a.year_value is not null and a.factor_id = 2 and a.in_active = TRUE) bb on parcel.parcel_id = bb.parcel_id 
where bb.parcel_id is null and parcel.geometry is not null 
--limit 10
)xxx where factor_value is not null
on conflict(parcel_id, year_value, factor_id, in_active) do nothing;
