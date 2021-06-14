
with new_update as (
select id, parcel_id, (select str_id from base.st_auto_street_select(10, 1, cpa.id)), 
(select * from base.st_street_line_parcel_side2( (select str_id from base.st_auto_street_select(10, 1, cpa.id)), cpa.id)) as street_side
from data_address.ca_parcel_address cpa 
where cpa.is_active is true and cpa.au3 = '0111963' and cpa.street_id is null and cpa.street_side is null and cpa.gn_geo_id is null
limit 250
)
update data_address.ca_parcel_address set street_id = s.str_id, street_side = s.street_side
from new_update s
where data_address.ca_parcel_address.id = s.id

