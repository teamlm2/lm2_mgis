drop view if exists admin_units.au_settlement_zone_view cascade;
CREATE OR REPLACE VIEW admin_units.au_settlement_zone_view AS 
select row_number() over() as id, z.code, z.name, p.polygon_geom as geometry from data_plan.pl_project_parcel p
join data_plan.cl_plan_zone z on p.plan_zone_id = z.plan_zone_id
where p.is_active = true and p.plan_zone_id = 381;
ALTER TABLE admin_units.au_settlement_zone_view
  OWNER TO geodb_admin;