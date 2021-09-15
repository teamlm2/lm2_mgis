Two methods to restore the database:

Method A
--------
1.) Create a database "darkhan" as copy of template_postgis.
2.) pg_restore -U postgres -d darkhan --disable-triggers dumps/schemas_and_data.dump

Method B
--------
1.) Create a database "darkhan" as copy of template_postgis.
2.) In support/aimag.txt write the 3-digits Aimag code (e.g. 045) of the Aimag(s)
    for which Soum schemas (sXXXXXX) are to be generated.
3.) Run shell script "3_create_schemas.sh"
4.) pg_restore -U postgres -d darkhan --disable-triggers dumps/data_only_part1.dump
5.) pg_restore -U postgres -d darkhan --disable-triggers dumps/data_only_part2.dump


To create the three dump files above run the commands as follows:

"schemas_and_data.dump":
------------------------
pg_dump -U geodb_admin -Fc -N public -N topology -N tiger darkhan > dumps/schemas_and_data.dump
pg_dump -U geodb_admin -Fc -N public -N topology -N tiger -N admin_units -N codelists -N data -N logging -N settings darkhan > dumps/schemas_and_data.dump
pg_restore -U postgres -d darkhan --disable-triggers dumps/data_only_part1.dump


"data_only_partX.dump"
----------------------
pg_dump -U geodb_admin -Fc -a -N public -N topology -N tiger -N codelists -N logging -N base -N settings darkhan > dumps/data_only_part1.dump
pg_dump -U geodb_admin -Fc -a -t settings.set_base* -t settings.set*zone darkhan > dumps/data_only_part2.dump


pg_dump -U postgres -Fc -n data_plan lm_0003 > /home/administrator/data_plan_20191014.dump
pg_dump -U postgres -h 192.168.15.6 -Fc -n data_address lm_0003 > D:/data_address.dump

postgres -D D:\work\pg_data


---------postgresql iin role-iig dump hiih sergeeh
pg_dumpall -h 127.0.0.1 -p 5432 -U postgres -v --globals-only > /home/administrator/useraccts.sql

psql -h 192.168.15.206 -d postgres -U postgres -f "/home/administrator/useraccts.sql"

pg_restore.exe --host "192.168.15.212" --port "5432" --username "postgres" --no-password --role "postgres" --dbname "lm_gns" --verbose "D:\\work\\DUMP_TEST\\ca_landuse_type_tbl.backup"

pg_dump -U geodb_admin -h 192.168.15.204 -Fc -N public -N topology -N tiger -N s04134 -N s04304 -N s04304s -N s04416 -N s04422 -N s04434 -N s04601 -N s04601_ol -N s04601_old -N s04816 -N s06216 -N s06216s -N s06410 -N s06413 -N s06546 -N s06728 -N s06746 -N s06749 -N s06749s -N s08301 -N s08313 -N s08316 -N s08410 -N s08507 -N s08546 -N data_monitoring_0720 -N sdplatform1 -N data_monitoring1 -N data_monitoring2 -N data_address_cd -N data_address_old -N data_monitoring_0720 -N data_monitoring_old -N data_plan1 -N data_plan_old lm_0003 > /alagac/lm_0003_2021-04-15-full.dump

