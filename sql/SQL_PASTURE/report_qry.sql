select * from (
select row_number() over(partition by gr.group_no) as rank, gr.group_no, gr.group_name, con.contract_no, con.contract_date, pg.code, au1.code||':'||au1.name as au1, au2.code||':'||au2.name as au2 from data_soums_union.ct_person_group gr
left join data_soums_union.ct_application_pug app_gr on gr.group_no = app_gr.group_no
left join data_soums_union.ct_app_group_boundary app_pg on app_gr.application = app_pg.application
left join data_soums_union.ca_pug_boundary pg on pg.code = app_pg.boundary_code
left join data_soums_union.ct_contract_application_role con_app on app_pg.application = con_app.application
left join data_soums_union.ct_contract con on con_app.contract = con.contract_id
left join admin_units.au_level2 au2 on gr.au2 = au2.code
left join admin_units.au_level1 au1 on au2.au1_code = au1.code
where gr.group_type = 1
order by au1.code, au2.code, gr.group_no
)xxx where rank = 1

-----------------------

select gr.group_no, gr.group_name, count(gm.person), au1.code||':'||au1.name as au1, au2.code||':'||au2.name as au2 from data_soums_union.ct_person_group gr
left join data_soums_union.ct_group_member gm on gr.group_no = gm.group_no
left join admin_units.au_level2 au2 on gr.au2 = au2.code
left join admin_units.au_level1 au1 on au2.au1_code = au1.code
where gr.group_type = 1
group by gr.group_no, gr.group_name, au2.code, au1.code
order by au1.code
-----------------------

select gr.group_no, gr.group_name, count(app_doc.document_id), au1.code||':'||au1.name as au1, au2.code||':'||au2.name as au2 from data_soums_union.ct_person_group gr
left join data_soums_union.ct_application_pug app_gr on gr.group_no = app_gr.group_no
left join data_soums_union.ct_app_group_boundary app_pg on app_gr.application = app_pg.application
left join data_soums_union.ca_pug_boundary pg on pg.code = app_pg.boundary_code
left join data_soums_union.ct_contract_application_role con_app on app_pg.application = con_app.application
left join data_soums_union.ct_contract con on con_app.contract = con.contract_id
left join data_soums_union.ct_application_document app_doc on app_pg.application = app_doc.application_id
left join admin_units.au_level2 au2 on gr.au2 = au2.code
left join admin_units.au_level1 au1 on au2.au1_code = au1.code
where gr.group_type = 1
group by gr.group_no, gr.group_name, au2.code, au1.code
order by au1.code, au2.code, gr.group_no


