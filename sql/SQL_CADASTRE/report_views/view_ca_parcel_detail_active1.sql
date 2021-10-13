-- Materialized View: data_soums_union.view_ca_parcel_detail_active_new

-- DROP MATERIALIZED VIEW data_soums_union.view_ca_parcel_detail_active_new;

CREATE MATERIALIZED VIEW data_soums_union.view_ca_parcel_detail_active_new AS 
 select sss.*, ccc.remainning_amount, ccc.paid_year_amount,
        ccc.total_amount,
        ccc.paid_total_amount,
        ccc.year_amount, 
        ccc.imposition_year,
        case 
            when ccc.contract_id is null then 'Ногдуулалт үүсгээгүй байна'
            else 'Ногдуулалт үүссэн'
        end as imposition_desc
        from (
        select row_number() over(partition by ddd.parcel_id order by ddd.decision_date desc, ddd.contract_date desc) as rank, * from (
        select row_number() over(partition by fff.parcel_id, fff.app_no, fff.contract_date) as ppp_rank, * from (
        select crt.code as rigth_type_code, 
        crt.description as rigth_type, cpt.parcel_id, 
        au1.code as au1_code,
        au1.name as au1_name,
        au2.code as au2_code,
        au2.name as au2_name,
        au3.code as au3_code,
        au3.name as au3_name,
        cpt.address_streetname ,
        cpt.address_khashaa,
        cpt.area_m2,  clt.code as landuse_code, clt.description landuse_desc, 
        satpr.is_owner, cpt2.code person_type_code, cpt2.description person_type_desc, cpr.code person_role_code, cpr.description person_role, bp.middle_name, bp.name, bp.first_name, bp.person_register, cdl.description as decision_level, cd.decision_id, cd.decision_no, cd.decision_date,
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
        cpt.au2, cpt.au3, ca.app_type app_type_code, cat.description as app_type_desc, cas.description as app_status, ca.app_id, ca.app_no, ca.approved_duration, ca.property_no, 
        case 
            when (select cae.mortgage_status from data_soums_union.ct_app8_ext cae 
                join data_soums_union.ct_application ca on cae.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) = 10 then true
            else false 
        end as is_mortgage,
        case 
            when (select cae.mortgage_status from data_soums_union.ct_app8_ext cae 
                join data_soums_union.ct_application ca on cae.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) = 10 then (select cae.end_mortgage_period from data_soums_union.ct_app8_ext cae 
                join data_soums_union.ct_application ca on cae.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1)
            else null 
        end as end_mortgage_period,
        case 	
            when (select cae2.court_status from data_soums_union.ct_app29_ext cae2  
                join data_soums_union.ct_application ca on cae2.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) = 30 or (select cae2.court_status from data_soums_union.ct_app29_ext cae2  
                join data_soums_union.ct_application ca on cae2.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) is null then false
            else true 
        end as is_court,
        case 	
            when (select cae2.court_status from data_soums_union.ct_app29_ext cae2  
                join data_soums_union.ct_application ca on cae2.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) = 30 or (select cae2.court_status from data_soums_union.ct_app29_ext cae2  
                join data_soums_union.ct_application ca on cae2.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) is null then null
            else (select cae2.court_decision_no from data_soums_union.ct_app29_ext cae2  
                join data_soums_union.ct_application ca on cae2.app_id = ca.app_id 
                where ca.parcel = cpt.parcel_id limit 1) 
        end as court_decision_no,
        cpt.geometry from data_soums_union.ca_parcel_tbl cpt
        join admin_units.au_level2 au2 on cpt.au2 = au2.code 
        join admin_units.au_level1 au1 on au2.au1_code = au1.code 
        left join admin_units.au_level3 au3 on cpt.au3 = au3.code 
        left join codelists.cl_landuse_type clt on cpt.landuse = clt.code 
        join data_soums_union.ct_application ca on cpt.parcel_id = ca.parcel 
        left join codelists.cl_application_type cat on ca.app_type = cat.code 
        join codelists.cl_application_status cas on ca.status_id = cas.code 
        join data_soums_union.ct_application_person_role capr on ca.app_id = capr.application 
        join codelists.cl_person_role cpr on capr.role = cpr.code 
        join base.bs_person bp on capr.person = bp.person_id 
        join codelists.cl_person_type cpt2 on bp.type = cpt2.code 
        join settings.set_application_type_person_role satpr on ca.app_type = satpr.type and capr.role = satpr.role
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
        where satpr.is_owner is true and 
        now() between cpt.valid_from and cpt.valid_till --and cpt.au2 = '06701' 
        --and cpt.parcel_id = '$parcelid'
        --and bp.person_id = '$personid'
        order by cd.decision_date desc 
        )fff order by fff.decision_date desc, fff.contract_date desc
        )ddd where ppp_rank = 1
        )sss 
        left join (select vrfn.remainning_amount,
        vrfn.paid_year_amount,
        vrfn.total_amount,
        vrfn.paid_total_amount,
        vrfn.year_amount, 
        vrfn.imposition_year,
        vrfn.contract_id from data_estimate.view_report_fee_new vrfn 
        where vrfn.imposition_year = date_part('year', now())) ccc on sss.contract_id = ccc.contract_id
        where rank = 1
WITH DATA;

ALTER TABLE data_soums_union.view_ca_parcel_detail_active_new
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO cadastre_update;
GRANT SELECT ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO cadastre_view;
GRANT SELECT ON TABLE data_soums_union.view_ca_parcel_detail_active_new TO reporting;
