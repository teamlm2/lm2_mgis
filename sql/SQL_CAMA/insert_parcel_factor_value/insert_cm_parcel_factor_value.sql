--# factor_id = 2; elevation
insert into data_cama.cm_parcel_factor_value(parcel_id, factor_id, factor_value, in_active, year_value, closets_parcel_id)

select parcel.parcel_id, 2, base.calculate_dem_cama_parcel(1, parcel.parcel_id), true, 2019, null from data_soums_union.ca_parcel_tbl parcel
where substring(parcel.au2, 1, 3) = '011' and parcel.geometry is not null
on conflict(parcel_id, year_value, factor_id, in_active) do nothing;

------------------
insert into data_cama.cm_parcel_factor_value(parcel_id, factor_id, factor_value, in_active, year_value, year_value)


--# factor_id = 2; elevation
insert into data_cama.cm_parcel_factor_value(parcel_id, factor_id, factor_value, in_active, year_value, closets_parcel_id)

select parcel.parcel_id, 2, base.calculate_dem_cama_parcel(1, parcel.parcel_id), true, 2019, null from data_soums_union.ca_parcel_tbl parcel
where parcel.au2 = '01107' and parcel.geometry is not null 
--limit 50
on conflict(parcel_id, year_value, factor_id, in_active) do nothing;


select parcel.parcel_id from data_soums_union.ca_parcel_tbl parcel
where parcel.au2 = '01101' and parcel.geometry is not null