__author__ = 'B.Ankhbold'

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from ClLanduseType import *
from Base import *


class ParcelSearch(Base):

    __tablename__ = 'parcel_search'

    parcel_id = Column(String, primary_key=True)
    person_role = Column(Integer)
    main_applicant = Column(Boolean)
    old_parcel_id = Column(Integer)
    geo_id = Column(String)
    person_id = Column(Integer)
    person_register = Column(String)
    name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    app_no = Column(String)
    decision_no = Column(String)
    contract_no = Column(String)
    record_no = Column(String)
    address_streetname = Column(String)
    address_khashaa = Column(String)
    au2_code = Column(String)
    contract_status = Column(Integer)
    record_status = Column(Integer)
    right_type_code = Column(Integer)
    right_type_desc = Column(String)

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")
