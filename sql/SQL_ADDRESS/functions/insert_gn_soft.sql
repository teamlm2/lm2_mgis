--SELECT * from dblink_connect('hostaddr=192.168.15.27 port=5432 dbname=lm_import user=lm_import_user password=123gazar!@#')

delete from data_address_import.gn_soft;

insert into data_address_import.gn_soft (geo_id, geo_data, feature_id, documentname, namedplacetype, majorlocaltype, mediumlocaltype, minorlocaltype,
leastdetailedviewingresolution, mostdetailedviewingresolution, "text", "language", script, transliterationscheme,transliteration, namestatus, documentnumber, documentdate,
organizationname, nameofemployee, employeeposition, guidename, "date", "namespace", versionid, gm_type, beginlifespanversion, endlifespanversion, validfrom, validto)

SELECT * FROM 
dblink('hostaddr=192.168.15.27 port=5432 dbname=lm_import user=lm_import_user password=123gazar!@#', 
'select geo_id, geo_data, feature_id, documentname, namedplacetype, majorlocaltype, mediumlocaltype, minorlocaltype,
leastdetailedviewingresolution, mostdetailedviewingresolution, "text", "language", script, transliterationscheme,transliteration, namestatus, documentnumber, documentdate,
organizationname, nameofemployee, employeeposition, guidename, "date", "namespace", versionid, gm_type, beginlifespanversion, endlifespanversion, validfrom, validto from public.gn_soft_new') AS 
t(geo_id text, geo_data geometry, feature_id int4, documentname text, namedplacetype text, majorlocaltype text, mediumlocaltype text, minorlocaltype text, leastdetailedviewingresolution text, mostdetailedviewingresolution text,
"text" text, "language" text, script text,transliterationscheme text,transliteration text, namestatus text, documentnumber text, documentdate text, organizationname text, nameofemployee text, employeeposition text,
guidename text, "date" text, "namespace" text, versionid text, gm_type text, beginlifespanversion text, endlifespanversion text, validfrom text, validto text)

ON CONFLICT (geo_id) DO nothing