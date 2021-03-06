
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClAddressSource import *
from ClAddressStatus import *
from AuZipCodeArea import *
from StStreet import *

class CaBuildingAddressHistory(Base):

    __tablename__ = 'ca_building_address_history'

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean)
    building_name = Column(String)
    address_parcel_no = Column(String)
    address_streetname = Column(String)
    address_building_no = Column(String)
    sort_value = Column(Integer)
    description = Column(String)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    valid_from = Column(Date)
    valid_till = Column(Date)

    # foreign keys:
    in_source = Column(Integer, ForeignKey('cl_address_source.code'))
    in_source_ref = relationship("ClAddressSource")

    zipcode_id = Column(Integer, ForeignKey('au_zipcode_area.code'))
    zipcode_id_ref = relationship("AuZipCodeArea")

    street_id = Column(Integer, ForeignKey('st_street.id'))
    street_id_ref = relationship("StStreet")

    au1 = Column(String, ForeignKey('au_level1.code'))
    au1_ref = relationship("AuLevel1")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    au3 = Column(String, ForeignKey('au_level3.code'))
    au3_ref = relationship("AuLevel3")

    khoroolol_id = Column(String, ForeignKey('au_khoroolol.fid'))
    khoroolol_id_ref = relationship("AuKhoroolol")

    building_id = Column(Integer, ForeignKey('ca_building_address.id'))
    building_ref = relationship("CaBuildingAddress")