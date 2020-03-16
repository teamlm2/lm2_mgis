--Bahiin hil
------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select gr.group_no, gr.group_name, gr.created_date, gr.au2, gr.boundary_code, public.st_asgeojson(geometry) as geometry 
from data_soums_union.ca_pug_boundary pug
inner join data_soums_union.ct_person_group gr on pug.code = gr.boundary_code) as t) to '/home/administrator/json/pug.json';

--Uliraliin hil
-------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select parcel_id, area_ga, pasture_type, public.st_asgeojson(geometry) as geometry 
from data_soums_union.ca_pasture_parcel_tbl) as t) to '/home/administrator/json/pasture.json';

--Person
-------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select gr.group_no, mb.role as group_role, pt.code as persontype, pt.description as persontypename, pr.name as lastname, pr.middle_name as surename, pr.first_name as firstname, pr.person_register, pr.phone 
from data_soums_union.ct_person_group gr 
inner join data_soums_union.ct_group_member mb on gr.group_no = mb.group_no
inner join base.bs_person pr on pr.person_id = mb.person
inner join codelists.cl_person_type pt on pr.type = pt.code) as t) to '/home/administrator/json/person.json';

--PointDetail
--------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select pd.point_detail_id, pd.register_date, pd.land_name, lf.code as landformcode, lf.description as landformname, pd.au2 
from pasture.ps_point_detail pd 
inner join pasture.cl_land_form lf on pd.land_form = lf.code) as t) to '/home/administrator/json/pointdetail.json';

--Point
--------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select mon.point_id, pd.point_detail_id, mon.valid_from, mon.valid_till,  public.st_asgeojson(mon.geometry) as geometry
from pasture.ca_pasture_monitoring mon
inner join pasture.ps_point_detail_points pd on mon.point_id = pd.point_id ) as t) to '/home/administrator/json/point.json';

--Urgats
-------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select ur.point_detail_id, bio.code as biomasstypecode, bio.description as biomasstypename, ur.value_year, ur.m_1, ur.m_1_value, ur.m_2, ur.m_2_value, ur.m_3, ur.m_3_value, ur.biomass_kg_ga 
from pasture.ps_point_urgats_value ur
inner join pasture.cl_biomass bio on bio.code = ur.biomass_type ) as t) to '/home/administrator/json/urgats.json';

--Pasture Value
------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select pv.point_detail_id, pt.code as pasturevaluecode, pt.description as pasturevaluename, pv.value_year, pv.current_value 
from pasture.ps_point_pasture_value pv
inner join pasture.cl_pasture_values pt on pv.pasture_value = pt.code) as t) to '/home/administrator/json/pasturevalue.json';

--Point Detail value
------------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select point_detail_id, monitoring_year, register_date, area_ga, duration, rc, rc_precent, sheep_unit, sheep_unit_plant, biomass, d1, d1_100ga, d2, d3, d3_rc, unelgee, rc_id, begin_month, end_month 
from pasture.ps_point_d_value) as t) to '/home/administrator/json/pointdetailvalue.json';


--Point Detail Image
-----------------
COPY (SELECT array_to_json(array_agg(row_to_json(t))) from (select pd.point_detail_id, pd.role, pd.monitoring_year, doc.name, doc.file_url from pasture.ps_point_document pd
 inner join data_soums_union.ct_document doc on pd.document_id = doc.id) as t) to '/home/administrator/json/pointdetailimage.json';