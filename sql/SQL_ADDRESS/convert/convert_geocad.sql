-------------parcel
truncate data_address.ca_parcel_address cascade;
insert into data_address.ca_parcel_address(parcel_id, is_active, in_source, address_parcel_no, address_streetname, address_neighbourhood, geographic_name, status, parcel_type, geometry)
select parcel_id, true, 1, address_khashaa, address_streetname, address_neighbourhood, address_neighbourhood, 2, 1, geometry from data_soums_union.ca_parcel_tbl
where now() between '1900-01-01'::date and valid_till;

-------------building
truncate data_address.ca_building_address cascade;
insert into data_address.ca_building_address(building_id, is_active, in_source, address_parcel_no, address_streetname, address_building_no, status, parcel_type, geometry)
select building_id, true, 1, address_khashaa, address_streetname, building_no, 2, 8, geometry from data_soums_union.ca_building_tbl
where now() between '1900-01-01'::date and valid_till;

-----------update parcel
with new_numbers as (
select g.id, p.new_khasha as address_parcel_no, new_addres as address_streetname, new_addr_1 as street_code from data_address.ca_parcel_address g, data_address.all_khashaa_last p 
where st_within(st_centroid(g.geometry), p.geom)
)
update data_address.ca_parcel_address set address_streetname= nn.address_streetname, address_parcel_no = nn.address_parcel_no, street_code = nn.street_code, parcel_type = 7, status = 4
from new_numbers nn
where data_address.ca_parcel_address.id = nn.id;

-----------update building
with new_numbers as (
select g.id, p.new_street as street_code, p.new_stre_1 as address_streetname, p.new_buildi as building_name, p.new_buil_1 as address_building_no from data_address.ca_building_address g, data_address.all_barilga_last p 
where st_within(st_centroid(g.geometry), p.geom) --limit 10
)
update data_address.ca_building_address set address_streetname= nn.address_streetname, address_building_no = nn.address_building_no, street_code = nn.street_code, building_name = nn.building_name, parcel_type = 10, status = 4
from new_numbers nn
where data_address.ca_building_address.id = nn.id;

-------------history parcel
truncate data_address.ca_parcel_address_history cascade;
insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, address_parcel_no, address_streetname, address_neighbourhood, geographic_name)
select id, is_active, in_source, address_parcel_no, address_streetname, address_neighbourhood, geographic_name from data_address.ca_parcel_address;

-------------history building
truncate data_address.ca_building_address_history cascade;
insert into data_address.ca_building_address_history(building_id, is_active, in_source, address_parcel_no, address_streetname, address_building_no)
select id, is_active, in_source, address_parcel_no, address_streetname, address_building_no from data_address.ca_building_address;

------------history update parcel
with new_numbers as (
select id from data_address.ca_parcel_address
where parcel_type = 7
)
update data_address.ca_parcel_address_history set is_active = false
from new_numbers nn
where data_address.ca_parcel_address_history.parcel_id = nn.id;

insert into data_address.ca_parcel_address_history(parcel_id, is_active, in_source, address_parcel_no, address_streetname, address_neighbourhood, geographic_name)
select id, is_active, in_source, address_parcel_no, address_streetname, address_neighbourhood, geographic_name from data_address.ca_parcel_address
where parcel_type = 7;

------------history update building
with new_numbers as (
select id from data_address.ca_building_address
where parcel_type = 10
)
update data_address.ca_building_address_history set is_active = false
from new_numbers nn
where data_address.ca_building_address_history.building_id = nn.id;

insert into data_address.ca_building_address_history(building_id, is_active, in_source, address_parcel_no, address_streetname, address_building_no)
select id, is_active, in_source, address_parcel_no, address_streetname, address_building_no from data_address.ca_building_address
where parcel_type = 10;