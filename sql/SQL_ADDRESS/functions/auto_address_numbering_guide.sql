
--Эхлээд бүх нэгж талбаруудыг тохирох гудамжинд хувиарлана

--Тухайн гудамжны эхлэлийн цэгийг олох
select * from data_address.st_street_point ssp 
where ssp.street_id = 137396 and point_type = 1

--Тухайн гудамжинд хамааралтай нэгж талбарууд   
select * from data_address.ca_parcel_address cpa 
where cpa.street_id = 137396

--