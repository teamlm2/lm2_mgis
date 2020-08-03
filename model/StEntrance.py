
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *
from ClEntryType import *
from ClAddressStatus import *
from AuZipCodeArea import *
from CaParcelAddress import *
from CaBuildingAddress import *
from StStreet import *

class StEntrance(Base):

    __tablename__ = 'st_entrance'

    entrance_id = Column(String, primary_key=True)
    code = Column(String)
    name = Column(String)
    address_entry_no = Column(String)
    is_active = Column(Boolean)
    address_parcel_no = Column(String)
    address_streetname = Column(String)
    address_neighbourhood = Column(String)
    geographic_name = Column(String)
    address_building_no = Column(String)
    description = Column(String)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POINT', 4326))

    # foreign keys:

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

    type = Column(String, ForeignKey('cl_entry_type.code'))
    type_ref = relationship("ClEntryType")

    parcel_id = Column(Integer, ForeignKey('ca_parcel_address.id'))
    parcel_ref = relationship("CaParcelAddress")

    building_id = Column(Integer, ForeignKey('ca_building_address.id'))
    building_ref = relationship("CaBuildingAddress")
