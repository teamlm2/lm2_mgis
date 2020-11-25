DROP TABLE if exists  data_landuse.st_mpa_zone_allow cascade;
CREATE TABLE data_landuse.st_mpa_zone_allow
(
  mpa_zone_id integer references admin_units.au_mpa_zone on update cascade on delete restrict,
  spa_type_id integer references codelists.cl_mpa_spa_type on update cascade on delete restrict,  
  description text,
  allow_type integer,
  id serial PRIMARY KEY,  
  is_active boolean NOT NULL DEFAULT true
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data_landuse.st_mpa_zone_allow
  OWNER TO geodb_admin;
GRANT ALL ON TABLE data_landuse.st_mpa_zone_allow TO geodb_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_mpa_zone_allow TO land_office_administration;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE data_landuse.st_mpa_zone_allow TO role_management;

insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 1, 1, 'Онгон бүсэд байгалийн унаган төрх, хэв шинжийг нь хадгалах шаардлагад нийцүүлж зөвхөн хамгаалалтын арга хэмжээ хэрэгжүүлнэ;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 1, 1, 'Онгон бүсэд байгалийн төлөв байдлыг нь хөндөхгүйгээр зөвхөн ажиглах хэлбэрээр судалгаа, шинжилгээний ажил явуулж болох бөгөөд үүнээс бусад үйл ажиллагаа явуулахыг хориглоно;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 2, 1, 'Хамгаалалтын бүсэд энэ хуулийн 9 дүгээр зүйлд зааснаас гадна ургамал, амьтны аймгийн өсч  үржих нөхцөлийг хангах, гамшгийн хор уршгийг арилгахтай холбогдсон биотехникийн арга хэмжээг байгаль орчинд сөрөг нөлөөгүй арга хэлбэрээр хэрэгжүүлнэ;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'хуулийн 9,10 дугаар зүйлд заасан үйл ажиллагаа; 2/ хөрс, ургамлын бүрхэвчийг нөхөн сэргээх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'ойд арчилгаа, цэвэрлэгээ хийх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'ан амьтны тооллого, тэдгээрийн тоо, нас, хүйс, сүргийн бүтцийг зохицуулах үйл ажиллагааг батлагдсан хөтөлбөр, аргачлалын дагуу явуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'рашаан, эмчилгээ, сувилгааны чанартай бусад эрдсийг ашиглах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'байгалийн аялал, жуулчлалыг тогтоосон зам, чиглэлээр зохих журмын дагуу зохион байгуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'аялагч, зөвшөөрөл бүхий бусад хүн түр буудаллах, отоглох, ажиглалт, судалгаа шинжилгээ хийх зориулалтаар зохих журмын дагуу барьсан орон байрыг ашиглах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'зураг авах, дууны болон дүрс бичлэг хийх, тэдгээрийг зохиол бүтээл туурвихад ашиглах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'уул,овоо тахих, уламжлалт зан үйлийн бусад ёслол үйлдэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, 5, 1, 'нутгийн оршин суугчид ахуйн хэрэгцээндээ зориулан байгалийн дагалт баялаг, эмийн болон хүнсний ургамлыг зохих журмын дагуу түүж ашиглах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'газар хагалах, ухах, тэсэлгээ хийх, ашигт малтмал хайх, олборлох, элс, хайрга чулуу авах, мод, зэгс, шагшуурга бэлтгэх, хязгаарлалтын бүсээс бусад газарт зам тавих зэргээр байгалийн төлөв байдлыг өөрчлөх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'байгалийн дагалт баялаг, эмийн, хүнсний болон техникийн зориулалттай ургамлыг үйлдвэрлэлийн зориулалтаар түүж бэлтгэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'хуулийн 11 дүгээр зүйлийн 4-т зааснаас өөр зориулалтаар ан амьтан агнах, барих, үргээх, тэдгээрийн үүр, ичээ, нүх, ноохойг хөндөх, эвдэж сүйтгэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'хортон шавьж, мэрэгчид, түймэртэй тэмцэх, тэдгээрээс сэргийлэх арга хэмжээнд байгаль орчинд сөрөг нөлөөлөх арга, техник, бодис хэрэглэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'хуулийн 11 дүгээр зүйлийн 7-д зааснаас өөр барилга байгууламж барих;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'хөрс, ус, агаар бохирдуулах аливаа үйл ажиллагаа явуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'тухайн газрын хамгаалалтын захиргааны зөвшөөрөлгүйгээр нохой дагуулж, буу авч явах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'аргагүйгээс бусад тохиолдолд тухайн газрын хамгаалалтын захиргаанаас урьдчилан авсан зөвшөөрөлгүйгээр агаарын хөлгөөр буулт хийх, хэт нам өндрөөр нислэг үйлдэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'өвөлжөө, хаваржаа, намаржаа, зуслангийн барилга байгууламж барих, зохих зөвшөөрөлгүйгээр мал бэлчээрлүүлэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'нуур, мөрөн, гол горхи, булаг, шанд зэрэг ил задгай усыг үйлдвэрлэлийн зориулалтаар ашиглах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(1, null, 2, 'хууль тогтоомж болон хамгаалалтын горимоор хориглосон байгаль орчинд сөрөг нөлөөлөх бусад үйл ажиллагаа явуулах;');
---
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 3, 1, 'Онцгой бүсэд байгалийн унаган төрхийг нь хадгалах шаардлагад нийцүүлэн хамгаалалтын арга хэмжээг хэрэгжүүлэхийн зэрэгцээ байгальд сөрөг нөлөөгүй арга, хэлбэрээр судалгаа, шинжилгээний ажил явуулах, ургамал, амьтны өсч үржих нөхцөлийг хангах, хөрсийг нөхөн сэргээх, гамшгийн хор уршгийг арилгах арга хэмжээ авна;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 4, 1, 'хуулийн 11,15 дугаар зүйлд заасан үйл ажиллагаа явуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 4, 1, 'зөвшөөрөгдсөн газар загас барих;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'хуулийн 11,15,16 дугаар зүйлд заасан үйл ажиллагаа;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'уламжлалт аргаар мал аж ахуй эрхлэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'аялагч, зөвшөөрөл бүхий бусад хүн ашиглах барилга байгууламжийг батлагдсан зураг, төсөл, зөвшөөрлийн дагуу барих;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'батлагдсан зураг төсөл, зохих журмын дагуу зам тавих, тээврийн хэрэгслийн зогсоол гаргах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'биеийн тамир, нийтийн арга хэмжээнд шаардагдах талбайг засч тохижуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, 5, 1, 'тухайн нутаг дэвсгэр дэх сууринг экологийн магадлан шинжилгээ хийж баталсан ерөнхий төлөвлөгөөний дагуу хөгжүүлэх;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, null, 2, 'хуулийн 12 дугаар зүйлийн 1-8, 11-т заасан үйл ажиллагаа явуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, null, 2, 'онцгой бүсэд энэ хуулийн 12 дугаар зүйлийн 9,1О-т заасан үйл ажиллагаа явуулах;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(2, null, 2, 'батлагдсан ерөнхий төлөвлөгөө, зураг төсвийг зөрчиж суурингийн нутаг дэвсгэрийг тэлэх, барилга байгууламж барих;');
---
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(3, null, 1, 'Байгалийн нөөц газарт хамгаалалтад авсан байгалийн хэв шинж, тодорхой баялгийн төрх байдал, ургамал, амьтны аймгийн байршил, өсөлт, үржилтэд сөрөг нөлөөгүйгээр уламжлалт аж ахуй эрхлэж болно;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(3, null, 1, 'Байгалийн нөөц газарт түүний байгаль орчинд сөрөг нөлөө үзүүлж болзошгүй барилга байгууламж барих, үйлдвэрлэлийн зориулалтаар газар ухах, тэсэлгээ хийх, ашигт малтмал хайх, олборлох, ан амьтан агнах, барих, мод, зэгс, шагшуурга бэлтгэх зэргээр байгалийн унаган төрхийг өөрчлөх, голын усыг бохирдуулах аливаа үйл ажиллагаа явуулахыг хориглоно;');
---
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(4, null, 1, 'Дурсгал газарт хаалт, хашлага барих, сэрэмжлүүлсэн дохио, тэмдэг тавих, түүний хамгаалалтыг нутгийн оршин суугчдад хариуцуулан өгөх зэргээр хамгаалалтын арга хэмжээ авна;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(4, null, 1, 'Дурсгалт газар дахь байгалийн болон түүх, соёлын дурсгалт зүйлээс О,1-З,О км-ийн орчимд сүр бараа, үзэмжийг нь дарах барилга байгууламж барих, газар хагалах, ухах, тэсэлгээ хийх, ашигт малтмал хайх, олборлох, байгалийн болон түүх, соёлын дурсгалт зүйлийг хөндөх, эвдэх, буулгах, тэдгээрт хохирол учруулахуйц бусад үйл ажиллагаа явуулахыг хориглоно;');
insert into data_landuse.st_mpa_zone_allow(spa_type_id, mpa_zone_id, allow_type, description) values(4, null, 1, 'Дэлхийн болон Үндэсний соёлын өвийн дурсгалт газрын хамгаалалтын дэглэмийг хуулиар тогтооно;');


