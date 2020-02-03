with new_numbers as (
select p.parcel_id, au3.code from data_soums_union.ca_parcel_tbl p 
join admin_units.au_level3 au3 on st_within(st_centroid(p.geometry), au3.geometry)
)
update data_soums_union.ca_parcel_tbl set au3 = nn.code
from new_numbers nn
where data_soums_union.ca_parcel_tbl.parcel_id = nn.parcel_id and data_soums_union.ca_parcel_tbl.au3 is null


select p.parcel_id, au3.code from data_soums_union.ca_parcel_tbl p
left join admin_units.au_level3 au3 on st_overlaps((p.geometry), au3.geometry)
where p.au3 is null