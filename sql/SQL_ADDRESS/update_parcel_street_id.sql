
with new_numbers as (
select split_part(address_streetname, '-', 1), split_part(address_streetname, '-', 2), str.name, str.code, str.id as str_id, p.id as p_id  from data_address.ca_parcel_address p, data_address.st_street str
where p.au2 = '01125' and str.au2 = '01125' and split_part(address_streetname, '-', 1) = str.name and split_part(address_streetname, '-', 2) = str.code
)
update data_address.ca_parcel_address
  set street_id = s.str_id
from new_numbers s
where data_address.ca_parcel_address.id = s.p_id and data_address.ca_parcel_address.au2 = '01125';