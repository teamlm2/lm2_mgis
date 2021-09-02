DROP MATERIALIZED VIEW if exists data_soums_union.view_ca_parcel_detail_active_new;
CREATE MATERIALIZED VIEW data_soums_union.view_ca_parcel_detail_active_new AS 

select * from (
select row_number() over(partition by ddd.parcel_id order by ddd.decision_date desc, ddd.contract_date desc) as rank, * from (
select row_number() over(partition by fff.parcel_id, fff.app_no, fff.contract_date) as ppp_rank, * from (
select crt.code as rigth_type_code, 
crt.description as rigth_type, cpt.parcel_id, 
cpt.address_streetname ,
cpt.address_khashaa,
cpt.area_m2,  clt.code as landuse_code, clt.description landuse_desc, 
cpt2.code person_type_code, cpt2.description person_type_desc,bp.middle_name, bp.name, bp.first_name, bp.person_register, cdl.description as decision_level, cd.decision_id, cd.decision_no, cd.decision_date,
case 
	when crt.code = 3 then cor.record_date 
	else cc.contract_date 
end as contract_date,
cc.contract_end, 
case 
	when crt.code = 3 then cor.record_id 
	else cc.contract_id 
end as contract_id, 
case 
	when crt.code = 3 then cor.record_no 
	else cc.contract_no 
end as contract_no, 
case 
	when crt.code = 3 then crs2.description 
	else ccs2.description
end as contract_status_desc, 
case 
	when crt.code = 3 then cor.certificate_no 
	else cc.certificate_no 
end as certificate_no, 
cpt.au2, cpt.au3, ca.app_type app_type_code, cat.description as app_type_desc, cas.description as app_status, ca.app_id, ca.app_no, ca.approved_duration, ca.property_no, cpt.geometry from data_soums_union.ca_parcel_tbl cpt
left join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
join data_soums_union.ct_application ca on cpt.parcel_id = ca.parcel 
left join codelists.cl_application_type cat on ca.app_type = cat.code 
join codelists.cl_application_status cas on ca.status_id = cas.code 
join data_soums_union.ct_application_person_role capr on ca.app_id = capr.application 
join base.bs_person bp on capr.person = bp.person_id 
join codelists.cl_person_type cpt2 on bp."type" = cpt2.code 
join settings.set_application_type_person_role satpr on ca.app_type = satpr."type" and capr."role" = satpr."role" 
join codelists.cl_right_type crt on ca.right_type = crt.code 
join data_soums_union.ct_decision_application cda on ca.app_id = cda.application 
join data_soums_union.ct_decision cd on cda.decision = cd.decision_id  
join codelists.cl_decision_level cdl on cd.decision_level = cdl.code 
left join data_soums_union.ct_contract_application_role ccar on ca.app_id = ccar.application 
left join data_soums_union.ct_contract cc on ccar.contract = cc.contract_id 
left join codelists.cl_contract_status ccs2 on cc.status = ccs2.code 
left join data_soums_union.ct_record_application_role crar on ca.app_id = crar.application 
left join data_soums_union.ct_ownership_record cor on crar.record = cor.record_id 
left join codelists.cl_record_status crs2 on cor.status = crs2.code 
where satpr.is_owner is true 
and now() between cpt.valid_from and cpt.valid_till --and cpt.au2 = '06701' and cpt.parcel_id = '6712016523'
order by cd.decision_date desc 
)fff order by fff.decision_date desc, fff.contract_date desc
)ddd where ppp_rank = 1
)sss where rank = 1;


ALTER TABLE data_soums_union.view_ca_parcel_detail_active_new
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO reporting;