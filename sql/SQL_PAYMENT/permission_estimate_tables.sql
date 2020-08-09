GRANT ALL ON TABLE data_estimate.pa_payment_paid TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_estimate.pa_payment_paid TO land_office_administration, contracting_update;
GRANT SELECT ON TABLE data_estimate.pa_payment_paid TO cadastre_view;
GRANT SELECT ON TABLE data_estimate.pa_payment_paid TO cadastre_update;
GRANT SELECT ON TABLE data_estimate.pa_payment_paid TO contracting_view;
GRANT SELECT ON TABLE data_estimate.pa_payment_paid TO contracting_update;
GRANT SELECT ON TABLE data_estimate.pa_payment_paid TO reporting;

GRANT ALL ON TABLE data_estimate.pa_imposition TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_estimate.pa_imposition TO land_office_administration, contracting_update;
GRANT SELECT ON TABLE data_estimate.pa_imposition TO cadastre_view;
GRANT SELECT ON TABLE data_estimate.pa_imposition TO cadastre_update;
GRANT SELECT ON TABLE data_estimate.pa_imposition TO contracting_view;
GRANT SELECT ON TABLE data_estimate.pa_imposition TO contracting_update;
GRANT SELECT ON TABLE data_estimate.pa_imposition TO reporting;

GRANT ALL ON SEQUENCE data_estimate.pa_payment_paid_id_seq TO geodb_admin;
GRANT USAGE ON SEQUENCE data_estimate.pa_payment_paid_id_seq TO contracting_update;
GRANT USAGE ON SEQUENCE data_estimate.pa_payment_paid_id_seq TO application_update;