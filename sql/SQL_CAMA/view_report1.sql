BEGIN;
 
   SELECT base.dynamic_pivot(
       'select a.parcel_id, f.name, a.factor_value from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id 
where parcel.au2 = '''||'01125'||''' order by a.parcel_id ', 'select DISTINCT f.name from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id
where f.landuse_type = 210401 or f.landuse_type = 210402 or f.landuse_type = 210501 or f.landuse_type = 210401 or f.landuse_type = 320301 or f.landuse_type = 340301 or f.landuse_type = 100001 or f.landuse_type = 340201
or f.id = 2 or f.id = 3
order by 1'
     ) AS cur;

FETCH ALL FROM "mycursor";

COMMIT;

----------
select DISTINCT f.name from data_cama.cm_parcel_factor_value a
join data_cama.cm_factor f on a.factor_id = f.id
join data_soums_union.ca_parcel_tbl parcel on a.parcel_id = parcel.parcel_id
where f.landuse_type = 210401 or f.landuse_type = 210402 or f.landuse_type = 210501 or f.landuse_type = 210401 or f.landuse_type = 320301 or f.landuse_type = 340301 or f.landuse_type = 100001
or f.id = 2 or f.id = 3
order by 1