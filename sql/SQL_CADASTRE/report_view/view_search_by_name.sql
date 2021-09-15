--create view search_by_name
CREATE OR REPLACE VIEW search_by_name AS 
SELECT 		row_number() over() as gid,
		a.geometry::geometry(Polygon,4326) AS geometry,
		a.parcel_id,
		a.old_parcel_id,
		a.address_khashaa,
		a.address_streetname,
		st_area(a.geometry)::integer AS area,
		x.parcel,
		x.person_id,
		x.name AS xxx,
		x.first_name
   FROM s06201.ca_parcel_tbl a
     LEFT JOIN ( SELECT 	
		a.parcel,
		g.person_id,
		g.name,
		g.first_name
					
		FROM s06201.ct_contract c,
		s06201.ct_application_person_role e,
		s06201.ct_contract_application_role b,
		base.bs_person g,
		s06201.ct_application a
	
WHERE c.contract_no = b.contract AND e.application = a.app_no AND e.person = g.id and e.application = b.application) x ON a.parcel_id::text = x.parcel::text;

ALTER TABLE search_by_name
  OWNER TO geodb_admin;

GRANT ALL ON TABLE search_by_name TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE search_by_name TO cadastre_update;
GRANT SELECT ON TABLE search_by_name TO cadastre_view;
GRANT SELECT ON TABLE search_by_name TO reporting;