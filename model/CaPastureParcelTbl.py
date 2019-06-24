
__author__ = 'B.Ankhbold'
from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ClLanduseType import *


class CaPastureParcelTbl(Base):

    __tablename__ = 'ca_pasture_parcel_tbl'

    parcel_id = Column(String, primary_key=True)
    old_parcel_id = Column(String)
    geo_id = Column(String)
    area_ga = Column(Float)
    capacity = Column(Float)
    address_neighbourhood = Column(String)
    pasture_type = Column(String)
    valid_from = Column(Date)
    valid_till = Column(Date)
    geometry = Column(Geometry('POLYGON', 4326))

    # foreign keys:
    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")

    #applications = relationship("CtApplication")

    au2 = Column(String, ForeignKey('au_level2.code'))
    au2_ref = relationship("AuLevel2")

    org_type = Column(String, ForeignKey('sd_organization.id'))
    org_type_ref = relationship("SdOrganization")

    group_type = Column(String, ForeignKey('cl_person_group_type.code'))
    group_type_ref = relationship("ClPersonGroupType")