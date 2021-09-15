insert into base.bs_person (type, name, middle_name, first_name,gender,person_register,phone,mobile_phone,address_street_name,address_khaskhaa)

select xxx.type,xxx.name,xxx.middle_name,xxx.first_name,xxx.gender,xxx.person_register,xxx.utas1,xxx.utas2,xxx.address_streetname,xxx.address_khashaa from
(select 
	case
		when p.heid = '1' and char_length(p.register) = 10 then 10
		when p.heid = '2' and char_length(p.register) = 7 then 30 
		when p.heid = '3' and char_length(p.register) = 7 then 40
		when p.heid = '4' then 50
		when (p.heid = '6' or p.heid = '5') then 60
		else 10
	end as type,
	case
		when p.heid::text = '2' or p.heid::text = '3' or p.heid::text = '6' or p.heid::text = '5' then p.ner
	
		when p.ovog is null then ' '
		else p.ovog
	end as name,
	p.ovogner as middle_name, 
	case 
		when p.heid = '2' or p.heid = '3' or p.heid = '6' or p.heid = '5' then ''
		when p.heid = '1' or p.heid = '4' then p.ner
		else '' 
	end as first_name,

	case
		when p.heid = '1' and char_length(p.register)=10 and ((substring(p.register,10,1))) = '0' and ((substring(p.register,10,1))) = '2' and ((substring(p.register,10,1))) = '4' and (substring(p.register,10,1)) = '6' and (substring(p.register,10,1)) = '8' then 2
		when p.heid = '1' and char_length(p.register)=10 and ((substring(p.register,10,1))) = '1' and ((substring(p.register,10,1))) = '3' and ((substring(p.register,10,1))) = '5' and ((substring(p.register,10,1))) = '7' and ((substring(p.register,10,1))) = '9' then 1	
		else 1
	end as gender,
	 p.register as person_register,
	 row_number() over (partition by p.register) as rank,
	p.utas1,
	p.utas2,
	p.gudamj address_streetname,
	case
		when char_length(p.hashaa::text) > 50 then ''
		else p.hashaa::text
	end as address_khashaa
	--p.hashaa address_khashaa
	
from data_ub.ca_mpa_parcel_edit p
where p.register IS NOT NULL and p.register != ' ' and p.ner is not null
and ((p.heid = '1' and char_length(p.register) = 10 and substring(p.register, 1,2) ~ '[а-яА-Я, a-zA-Z]')
or ((p.heid = '2' or p.heid = '3') and char_length(p.register) = 7 and p.register ~ '^([0-9]+\.?[0-9]*|\.[0-9]+)$')
or p.heid = '6' or p.heid = '5' or p.heid = '4')
and is_finish is null
)xxx  where rank = 1 and person_register not in (select person_register from base.bs_person);

--on conflict(person_register) do nothing;